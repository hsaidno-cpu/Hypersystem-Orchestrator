"""P0 Codex CLI adapter contract and security regression tests."""
from __future__ import annotations
import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from tools import codex_skill_host_adapter as adapter

GOOD={
 "case_id":"HSO-P0-SKILL-ANALYZER-001","skill_name":"skill-analyzer",
 "methods":[{"method":"threat modeling","purpose":"map attack paths"},{"method":"root cause analysis","purpose":"identify control failures"}],
 "observed_facts":["Cache files are persistent.","Multiple local users can write the cache directory."],
 "inferences":["Other local users may obtain cached responses."],
 "unknowns":["The exact OS ACL and deployment topology are not supplied."],
 "root_causes":["Shared writable storage lacks access and lifecycle controls."],
 "risk_findings":["A local user may read cached responses.","Indefinite retention increases exposure duration."],
 "mitigations":["Apply per-user access controls and encryption.","Set retention, expiry and secure deletion."],
 "verification_tests":["Verify a second OS user cannot read cache contents.","Verify expired cache entries are deleted."],
 "completion_status":"completed"
}
FAKE=r'''#!/usr/bin/env python3
import json,os,pathlib,sys
if sys.argv[1:]==["--version"]: print("codex-cli 0.171.0");raise SystemExit(0)
if sys.argv[1:3]==["exec","--help"]: print("--model --json --ephemeral --sandbox --ask-for-approval --output-schema --output-last-message");raise SystemExit(0)
args=sys.argv[2:]
def val(k):return args[args.index(k)+1]
assert val("--model")=="gpt-6.2-sol" and "--json" in args and "--ephemeral" in args
assert val("--sandbox")=="read-only" and val("--ask-for-approval")=="never"
assert "$skill-analyzer" in args[-1] and os.environ["CODEX_API_KEY"]=="unit-test-api-key"
assert "HSO_APPROVAL_HMAC_KEY" not in os.environ and "GITHUB_TOKEN" not in os.environ
cfg=(pathlib.Path(os.environ["CODEX_HOME"])/"config.toml").read_text()
for x in ('"*_KEY" = "exclude"','"*_TOKEN" = "exclude"','"*_SECRET" = "exclude"','"GITHUB_*" = "exclude"'):assert x in cfg
skills=pathlib.Path.cwd()/".agents"/"skills"
assert (skills/"skill-analyzer"/"SKILL.md").is_file() and (skills/"analyzer"/"SKILL.md").is_file()
assert not (skills/"skill-analyzer").is_symlink()
assert not (skills/"analyzer").is_symlink()
pathlib.Path(val("--output-last-message")).write_text(json.dumps(OUTPUT),encoding="utf-8")
print(json.dumps({"type":"thread.started","thread_id":"thr-test"}),flush=True)
print(json.dumps({"type":"turn.started","turn_id":"turn-test"}),flush=True)
print(json.dumps({"type":"item.completed","item":{"id":"m1","type":"agent_message","text":"structured"}}),flush=True)
if FAIL:
 print(json.dumps({"type":"turn.failed","turn_id":"turn-test"}),flush=True);raise SystemExit(1)
print(json.dumps({"type":"turn.completed","turn_id":"turn-test","status":"completed","usage":{"input_tokens":100,"cached_input_tokens":20,"output_tokens":30}}),flush=True)
'''
class CodexSkillHostAdapterTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  (self.root/"contracts").mkdir()
  (self.root/adapter.OUTPUT_SCHEMA_RELATIVE_PATH).write_text(json.dumps(adapter.PILOT_OUTPUT_SCHEMA),encoding="utf-8")
  child=self.root/"plugins"/"skill-analyzer";skills=child/"skills"
  for name in ("skill-analyzer","analyzer"):
   (skills/name).mkdir(parents=True);(skills/name/"SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n# {name}\n")
  (child/"plugin.json").write_text(json.dumps({"name":"skill-analyzer","version":"1.3.0","skills":"./skills"}))
  self.binary=self.root/"codex-fake";self._fake(GOOD)
 def tearDown(self):self.temp.cleanup()
 def _fake(self,result,fail=False):
  self.binary.write_text("#!/usr/bin/env python3\nOUTPUT="+repr(result)+"\nFAIL="+repr(fail)+"\n"+FAKE.split("\n",1)[1]);self.binary.chmod(0o755)
 def _env(self):
  return patch.dict(os.environ,{"CODEX_API_KEY":"unit-test-api-key","CODEX_BIN":str(self.binary),
   "HSO_APPROVAL_HMAC_KEY":"do-not-forward-this","GITHUB_TOKEN":"do-not-forward-token"},clear=False)
 def _payload(self):
  return {"skill_name":adapter.PLUGIN_KEY,"plugin_id":adapter.PLUGIN_ID,
   "skill_source_path":adapter.SKILL_RELATIVE_PATH.as_posix(),
   "request":"Analyze this synthetic cache risk with evidence, methods, root causes, mitigations and verification tests.",
   "approval_receipt":{"approver":"hsaidno-cpu","nonce":"test-nonce"}}
 def test_preflight_ready_with_limitations_without_inference(self):
  with self._env(),patch.object(adapter,"_source_commit",return_value=adapter.SOURCE_PIN):
   x=adapter.probe_codex_skill_host(self.root,adapter.SKILL_RELATIVE_PATH.as_posix())
  self.assertEqual(x["status"],"READY_WITH_LIMITATIONS");self.assertFalse(x["billable_inference_performed"])
  self.assertNotIn("unit-test-api-key",json.dumps(x))
 def test_missing_key_or_cli_blocks_preflight(self):
  with patch.dict(os.environ,{"CODEX_BIN":str(self.binary)},clear=True):
   self.assertEqual(adapter.probe_codex_skill_host(self.root,adapter.SKILL_RELATIVE_PATH.as_posix())["status"],"NOT_CONFIGURED")
 def test_exact_pin_is_required(self):
  with self._env(),patch.object(adapter,"_source_commit",return_value="0"*40):
   self.assertEqual(adapter.probe_codex_skill_host(self.root,adapter.SKILL_RELATIVE_PATH.as_posix())["status"],"UNAVAILABLE")
 def test_invocation_returns_thread_turn_usage_and_digest_receipt(self):
  with self._env(),patch.object(adapter,"_source_commit",return_value=adapter.SOURCE_PIN):
   result=adapter.invoke_codex_skill(self.root,"artifacts/result.json",self._payload(),{})
  target=self.root/"artifacts"/"result.json";obj=json.loads(target.read_text());r=obj["invocation_receipt"]
  self.assertEqual(result["thread_id"],"thr-test");self.assertEqual(r["session"]["turn_id"],"turn-test")
  self.assertEqual(r["usage"]["input_tokens"],100);self.assertEqual(r["model"],"gpt-6.2-sol")
  self.assertEqual(r["plugin"]["source_commit"],adapter.SOURCE_PIN)
  self.assertEqual(r["dispatch"]["skill_load_attestation"],"NO_DEDICATED_CLI_EVENT_EXPOSED")
  self.assertEqual(result["sha256"],adapter.sha256_file(target));self.assertFalse((self.root/".agents").exists())
  self.assertNotIn("unit-test-api-key",target.read_text())
 def test_failed_turn_has_no_invocation_artifact(self):
  self._fake(GOOD,True)
  with self._env(),patch.object(adapter,"_source_commit",return_value=adapter.SOURCE_PIN):
   with self.assertRaisesRegex(RuntimeError,"status 1"):adapter.invoke_codex_skill(self.root,"artifacts/fail.json",self._payload(),{})
  self.assertFalse((self.root/"artifacts"/"fail.json").exists())
 def test_bad_json_shape_or_unapproved_identity_fails_closed(self):
  self._fake({"wrong":"shape"})
  with self._env(),patch.object(adapter,"_source_commit",return_value=adapter.SOURCE_PIN):
   with self.assertRaises(Exception):adapter.invoke_codex_skill(self.root,"bad.json",self._payload(),{})
   p=self._payload();p["plugin_id"]="other"
   with self.assertRaisesRegex(RuntimeError,"identity mismatch"):adapter.invoke_codex_skill(self.root,"bad2.json",p,{})
 def test_canonical_schema_is_required_and_strict(self):
  self.assertEqual(adapter._load_schema(self.root),adapter.PILOT_OUTPUT_SCHEMA)
  (self.root/adapter.OUTPUT_SCHEMA_RELATIVE_PATH).unlink()
  with self.assertRaisesRegex(RuntimeError,"missing or unsafe"):adapter._load_schema(self.root)
 def test_paths_cannot_overwrite_or_escape_symlink(self):
  p=self.root/"protected.json";p.write_text("safe")
  with self.assertRaises(FileExistsError):adapter._safe_write(self.root,"protected.json","no")
  outside=self.root/"outside";outside.mkdir();(self.root/"link").symlink_to(outside,target_is_directory=True)
  with self.assertRaisesRegex(RuntimeError,"symlinks"):adapter._safe_write(self.root,"link/out.json","bad")
if __name__=="__main__":unittest.main()
