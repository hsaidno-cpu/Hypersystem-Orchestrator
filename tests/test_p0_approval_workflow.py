"""Tests for the short-lived owner-approved P0 workflow gate."""
from __future__ import annotations
import datetime,hashlib,hmac,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools import issue_p0_skill_approval as issue
from tools import prepare_p0_skill_workflow as prepare
SECRET="unit-test-key-with-sufficient-entropy-123456"
ACTOR="hsaidno-cpu";RUN="123456789"
def make_receipt():
 now=datetime.datetime.now(datetime.timezone.utc)
 unsigned={"case_id":issue.CASE_ID,"action_id":issue.ACTION_ID,"target_path":issue.TARGET_PATH,"authority":"S4",
 "approver":ACTOR,"issued_at":now.isoformat(timespec="seconds").replace("+00:00","Z"),
 "expires_at":(now+datetime.timedelta(minutes=5)).isoformat(timespec="seconds").replace("+00:00","Z"),
 "nonce":"unit-nonce-123456","workflow_run_id":RUN,"workflow_run_attempt":"1"}
 canonical=json.dumps(unsigned,sort_keys=True,separators=(",",":"),ensure_ascii=False)
 return {**unsigned,"signature":hmac.new(SECRET.encode(),canonical.encode(),hashlib.sha256).hexdigest()}
class P0ApprovalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.approval=self.root/"approval.json";self.output=self.root/"workflow.json";self.template=self.root/"template.json"
  self.template.write_text(json.dumps({"schema_version":"1.0.0","case_id":issue.CASE_ID,"requested_by":"manual",
   "action_authority":"S4","environment":"SANDBOX","work_packages":[{"package_id":"WP-P0-SKILL-ANALYZER-INVOKE",
   "task_type":"plugin.skill_analyzer_p0_pilot","action_id":issue.ACTION_ID,"target_path":issue.TARGET_PATH,
   "input":{},"depends_on":[],"idempotency_key":"template","expected_sha256":"0"*64,"max_attempts":1,
   "recovery":{"on_action_failure":"NONE","on_verification_failure":"NONE"}}]}))
 def tearDown(self):self.tmp.cleanup()
 def _issue(self,extra=None):
  env={"HSO_APPROVAL_HMAC_KEY":SECRET,"GITHUB_ACTOR":ACTOR,"GITHUB_RUN_ID":RUN,"GITHUB_RUN_ATTEMPT":"1"};env.update(extra or {})
  with patch.dict(os.environ,env,clear=True),patch.object(sys,"argv",["issue","--output",str(self.approval)]):return issue.main()
 def _prepare(self,approval,extra=None):
  self.approval.write_text(json.dumps(approval))
  env={"GITHUB_ACTOR":ACTOR,"GITHUB_RUN_ID":RUN,"GITHUB_RUN_ATTEMPT":"1"};env.update(extra or {})
  with patch.dict(os.environ,env,clear=True),patch.object(sys,"argv",["prepare","--approval-receipt",str(self.approval),"--output",str(self.output)]),patch.object(prepare,"TEMPLATE",self.template):return prepare.main()
 def test_issue_creates_signed_five_minute_receipt(self):
  self._issue();r=json.loads(self.approval.read_text());unsigned={k:v for k,v in r.items() if k!="signature"}
  c=json.dumps(unsigned,sort_keys=True,separators=(",",":"),ensure_ascii=False)
  self.assertTrue(hmac.compare_digest(r["signature"],hmac.new(SECRET.encode(),c.encode(),hashlib.sha256).hexdigest()))
  start=datetime.datetime.fromisoformat(r["issued_at"].replace("Z","+00:00"));end=datetime.datetime.fromisoformat(r["expires_at"].replace("Z","+00:00"))
  self.assertAlmostEqual((end-start).total_seconds(),300,delta=2)
  self.assertEqual(self.approval.stat().st_mode&0o777,0o600)
 def test_issue_rejects_wrong_actor_and_rerun(self):
  with self.assertRaises(SystemExit):self._issue({"GITHUB_ACTOR":"other"})
  with self.assertRaises(SystemExit):self._issue({"GITHUB_RUN_ATTEMPT":"2"})
 def test_prepare_binds_approval_and_run_id(self):
  self._prepare(make_receipt());r=json.loads(self.output.read_text())
  self.assertEqual(r["requested_by"],ACTOR);self.assertEqual(r["work_packages"][0]["idempotency_key"],"hso-p0-skill-analyzer-"+RUN)
  self.assertEqual(r["work_packages"][0]["approval_receipt"]["nonce"],"unit-nonce-123456")
 def test_prepare_rejects_wrong_actor_scope_expiry_and_overwrite(self):
  with self.assertRaises(SystemExit):self._prepare(make_receipt(),{"GITHUB_ACTOR":"other"})
  wrong=make_receipt();wrong["target_path"]="other"
  with self.assertRaises(SystemExit):self._prepare(wrong)
  expired=make_receipt();expired["expires_at"]="2000-01-01T00:00:00Z"
  with self.assertRaises(SystemExit):self._prepare(expired)
  self.output.write_text("protected")
  with self.assertRaises(SystemExit):self._prepare(make_receipt())
if __name__=="__main__":unittest.main()
