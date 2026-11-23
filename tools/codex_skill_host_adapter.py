#!/usr/bin/env python3
"""P0 HSO adapter: one pinned SKILL ANALYZER Agent Skill through Codex CLI exec."""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tempfile, uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

PLUGIN_ID="plugins_6ae2a122f5c881919193c9b0ba51961e"
PLUGIN_KEY="skill-analyzer"
PLUGIN_VERSION="1.3.0"
SOURCE_REPOSITORY="hsaidno-cpu/skill-analyzer"
SOURCE_PIN="c469af7977c9bf6dcb3f5ab7b085a6de20d87004"
CODEX_VERSION_REQUIRED="0.171.0"
CODEX_MODEL="gpt-6.2-sol"
SKILL_RELATIVE_PATH=Path("plugins/skill-analyzer/skills/skill-analyzer/SKILL.md")
PLUGIN_MANIFEST_RELATIVE_PATH=Path("plugins/skill-analyzer/plugin.json")
SKILLS_SOURCE_ROOT=Path("plugins/skill-analyzer/skills")
OUTPUT_SCHEMA_RELATIVE_PATH=Path("contracts/hso-p0-skill-analysis-output.schema.json")
MAX_OUTPUT_CHARS=30000
MAX_JSONL_BYTES=4_000_000

PILOT_OUTPUT_SCHEMA: dict[str,Any]={
 "type":"object","additionalProperties":False,
 "required":["case_id","skill_name","methods","observed_facts","inferences","unknowns","root_causes","risk_findings","mitigations","verification_tests","completion_status"],
 "properties":{
  "case_id":{"const":"HSO-P0-SKILL-ANALYZER-001"},
  "skill_name":{"const":PLUGIN_KEY},
  "methods":{"type":"array","minItems":2,"maxItems":4,"items":{"type":"object","additionalProperties":False,"required":["method","purpose"],"properties":{"method":{"type":"string"},"purpose":{"type":"string"}}}},
  "observed_facts":{"type":"array","minItems":2,"items":{"type":"string"}},
  "inferences":{"type":"array","items":{"type":"string"}},
  "unknowns":{"type":"array","minItems":1,"items":{"type":"string"}},
  "root_causes":{"type":"array","minItems":1,"items":{"type":"string"}},
  "risk_findings":{"type":"array","minItems":2,"items":{"type":"string"}},
  "mitigations":{"type":"array","minItems":2,"items":{"type":"string"}},
  "verification_tests":{"type":"array","minItems":2,"items":{"type":"string"}},
  "completion_status":{"const":"completed"}
 }
}

def utc_now()->str:
 return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")

def canonical_json(v:Any)->str:
 return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha256_bytes(b:bytes)->str:
 return hashlib.sha256(b).hexdigest()

def sha256_file(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()

def _clean(s:Any,limit:int=1000)->str:
 return str(s).replace("\x00","")[:limit]

def _binary()->str|None:
 explicit=os.environ.get("CODEX_BIN")
 if explicit:
  p=Path(explicit)
  return str(p) if p.is_file() and os.access(p,os.X_OK) else None
 return shutil.which("codex")

def _base_env(codex_home:Path,home:Path,tmp:Path,api_key:str|None=None)->dict[str,str]:
 src=os.environ
 env={k:src[k] for k in ("PATH","LANG","LC_ALL","TERM","CI","USER","LOGNAME","SHELL") if src.get(k)}
 env.update({"CODEX_HOME":str(codex_home),"HOME":str(home),"USERPROFILE":str(home),"TMPDIR":str(tmp),"NO_COLOR":"1","CODEX_TELEMETRY":"0"})
 if api_key: env["CODEX_API_KEY"]=api_key
 return env

def _write_config(home:Path)->Path:
 home.mkdir(mode=0o700,parents=True,exist_ok=True)
 p=home/"config.toml"
 p.write_text(
  'approval_policy = "never"\n'
  'sandbox_mode = "read-only"\n'
  'web_search = "disabled"\n'
  '[shell_environment_policy]\n'
  'inherit = "core"\n'
  'ignore_default_excludes = false\n'
  '[shell_environment_policy.filters]\n'
  '"*_KEY" = "exclude"\n'
  '"*_TOKEN" = "exclude"\n'
  '"*_SECRET" = "exclude"\n'
  '"GITHUB_*" = "exclude"\n',encoding="utf-8")
 try:p.chmod(0o600)
 except OSError:pass
 return p

def _resolve_skill(workspace:Path,skill_source_path:str)->Path:
 if skill_source_path!=SKILL_RELATIVE_PATH.as_posix():
  raise RuntimeError("P0 accepts only the pinned SKILL ANALYZER master skill path")
 root=workspace.resolve(); cur=root
 for part in SKILL_RELATIVE_PATH.parts:
  cur=cur/part
  if cur.is_symlink():raise RuntimeError("canonical skill path cannot traverse a symbolic link")
 p=cur.resolve(strict=True)
 try:p.relative_to(root)
 except ValueError as e:raise RuntimeError("skill path escapes workspace") from e
 if not p.is_file():raise RuntimeError("canonical SKILL ANALYZER skill is not a regular file")
 return p

def _manifest(workspace:Path)->dict[str,Any]:
 p=workspace/PLUGIN_MANIFEST_RELATIVE_PATH
 if p.is_symlink():raise RuntimeError("plugin manifest cannot be a symbolic link")
 m=json.loads(p.read_text(encoding="utf-8"))
 if m.get("name")!=PLUGIN_KEY or m.get("version")!=PLUGIN_VERSION or m.get("skills")!="./skills":
  raise RuntimeError("pinned plugin manifest identity/version/layout mismatch")
 return m

def _source_commit(workspace:Path)->str:
 env={k:v for k,v in os.environ.items() if not (k.endswith("_KEY") or k.endswith("_TOKEN") or k.endswith("_SECRET") or k.startswith("GITHUB_"))}
 p=subprocess.run(["git","-C",str(workspace/"plugins/skill-analyzer"),"rev-parse","HEAD"],capture_output=True,text=True,timeout=10,env=env)
 commit=p.stdout.strip()
 if p.returncode!=0 or commit!=SOURCE_PIN:raise RuntimeError("SKILL ANALYZER submodule is not at the approved immutable source pin")
 return commit

def _codex_version(binary:str,env:dict[str,str])->str:
 p=subprocess.run([binary,"--version"],capture_output=True,text=True,timeout=20,env=env)
 if p.returncode:raise RuntimeError("Codex CLI version probe failed")
 version=(p.stdout or p.stderr).strip().splitlines()
 if not version:raise RuntimeError("Codex CLI returned an empty version")
 v=version[0].strip()
 if v not in {f"codex-cli {CODEX_VERSION_REQUIRED}",f"codex {CODEX_VERSION_REQUIRED}"}:
  raise RuntimeError(f"Codex CLI version mismatch; expected {CODEX_VERSION_REQUIRED}, observed {_clean(v,100)}")
 return v

def _codex_help(binary:str,env:dict[str,str])->str:
 p=subprocess.run([binary,"exec","--help"],capture_output=True,text=True,timeout=20,env=env)
 if p.returncode:raise RuntimeError("Codex CLI exec help probe failed")
 h=(p.stdout or "")+"\n"+(p.stderr or "")
 missing=[x for x in ("--model","--json","--ephemeral","--sandbox","--ask-for-approval","--output-schema","--output-last-message") if x not in h]
 if missing:raise RuntimeError("Codex CLI lacks required P0 flags: "+", ".join(missing))
 return h

def _load_schema(workspace:Path)->dict[str,Any]:
 p=workspace/OUTPUT_SCHEMA_RELATIVE_PATH
 if p.is_symlink() or not p.is_file():raise RuntimeError("canonical P0 output schema is missing or unsafe")
 try:
  schema=json.loads(p.read_text(encoding="utf-8"));Draft202012Validator.check_schema(schema)
 except Exception as e:raise RuntimeError(f"canonical P0 output schema is invalid: {e}") from e
 if schema.get("type")!="object" or schema.get("additionalProperties") is not False:
  raise RuntimeError("P0 output schema must require a strict JSON object")
 return schema

def probe_codex_skill_host(workspace:Path,skill_source_path:str)->dict[str,Any]:
 api=os.environ.get("CODEX_API_KEY","").strip();binary=_binary()
 if not api:return {"status":"NOT_CONFIGURED","evidence":"CODEX_API_KEY is not configured"}
 if not binary:return {"status":"NOT_CONFIGURED","evidence":"Codex CLI binary is not installed"}
 try:
  skill=_resolve_skill(workspace,skill_source_path);manifest=_manifest(workspace);schema=_load_schema(workspace);commit=_source_commit(workspace)
  with tempfile.TemporaryDirectory(prefix="hso-codex-probe-") as t:
   root=Path(t);home=root/"home";tmp=root/"tmp";home.mkdir(mode=0o700);tmp.mkdir(mode=0o700)
   codex_home=root/"codex-home";_write_config(codex_home)
   env=_base_env(codex_home,home,tmp)
   version=_codex_version(binary,env);_codex_help(binary,env)
  return {"status":"READY_WITH_LIMITATIONS","evidence":"pinned skill, schema, Codex CLI version and required flags verified; API key presence checked but provider entitlement/authentication not tested; no inference issued",
   "host":"codex-cli-exec","codex_cli_version":version,"model":CODEX_MODEL,
   "source_commit":commit,"skill_sha256":sha256_file(skill),"plugin_version":manifest["version"],
   "output_schema_sha256":sha256_bytes(canonical_json(schema).encode()),"billable_inference_performed":False}
 except Exception as e:return {"status":"UNAVAILABLE","evidence":_clean(f"Codex CLI preflight failed: {type(e).__name__}: {e}")}

def _register_skills(workspace:Path)->tuple[Path,list[Path],list[Path]]:
 agents=workspace/".agents";repo=agents/"skills";created=[];links=[]
 if not agents.exists():agents.mkdir();created.append(agents)
 if not repo.exists():repo.mkdir();created.append(repo)
 if repo.is_symlink() or not repo.is_dir():raise RuntimeError(".agents/skills is not a regular directory")
 src=workspace/SKILLS_SOURCE_ROOT
 if not src.is_dir() or src.is_symlink():raise RuntimeError("canonical plugin skills directory is unavailable")
 try:
  for d in sorted(src.iterdir()):
   if not d.is_dir() or not (d/"SKILL.md").is_file():continue
   target=repo/d.name
   if target.exists() or target.is_symlink():raise RuntimeError(f"Codex skill name collision: {d.name}")
   target.symlink_to(d.resolve(),target_is_directory=True);links.append(target)
  if not any(x.name==PLUGIN_KEY for x in links):raise RuntimeError("master skill not registered for Codex discovery")
  return repo,links,created
 except Exception:
  _cleanup_links(links,created);raise

def _cleanup_links(links:list[Path],created:list[Path])->None:
 for link in links:
  try:
   if link.is_symlink():link.unlink()
  except OSError:pass
 for d in reversed(created):
  try:d.rmdir()
  except OSError:pass

def _safe_write(workspace:Path,relative:str,content:str)->tuple[Path,str]:
 part=Path(relative)
 if not relative or part.is_absolute() or any(x in {".",".."} for x in part.parts):raise RuntimeError("artifact path must be a safe relative path")
 root=workspace.resolve();cur=root
 for x in part.parts:
  cur=cur/x
  if cur.is_symlink():raise RuntimeError("artifact path cannot traverse symlinks")
 target=cur.resolve(strict=False)
 try:target.relative_to(root)
 except ValueError as e:raise RuntimeError("artifact escapes workspace") from e
 target.parent.mkdir(parents=True,exist_ok=True);raw=content.encode("utf-8")
 with target.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
 return target,sha256_bytes(raw)

def _events(text:str)->dict[str,Any]:
 if len(text.encode())>MAX_JSONL_BYTES:raise RuntimeError("Codex JSONL exceeds size limit")
 counts:Counter[str]=Counter();items:Counter[str]=Counter();thread=None;turn=None;status=None;errors=[];usage={}
 for line in text.splitlines():
  if not line.strip():continue
  try:e=json.loads(line)
  except json.JSONDecodeError as ex:raise RuntimeError("Codex JSONL event malformed") from ex
  if not isinstance(e,dict):continue
  typ=e.get("type")
  if isinstance(typ,str):counts[typ]+=1
  item=e.get("item")
  if typ in {"item.started","item.updated","item.completed"} and isinstance(item,dict) and isinstance(item.get("type"),str):items[item["type"]]+=1
  if typ=="thread.started":thread=e.get("thread_id") or thread
  elif typ=="turn.started":turn=e.get("turn_id") or turn
  elif typ=="turn.completed":
   turn=e.get("turn_id") or turn;status=e.get("status") or e.get("turn_status") or status
   u=e.get("usage")
   if isinstance(u,dict):
    usage={k:v for k,v in u.items() if k in {"input_tokens","cached_input_tokens","output_tokens"} and isinstance(v,int) and v>=0}
  elif typ in {"turn.failed","error"}:errors.append(typ)
 if not thread:raise RuntimeError("Codex JSONL has no thread.started event")
 if counts["turn.completed"]==0:raise RuntimeError("Codex JSONL has no turn.completed event")
 if items["agent_message"]==0:raise RuntimeError("Codex JSONL has no completed agent_message")
 if errors:raise RuntimeError("Codex JSONL contains failed event: "+", ".join(errors))
 return {"thread_id":thread,"turn_id":turn or "not-exposed-by-cli-jsonl","turn_status":status or "completed",
         "event_counts":dict(counts),"item_type_counts":dict(items),"usage":usage}

def invoke_codex_skill(workspace:Path,target_path:str,payload:dict[str,Any],context:dict[str,Any])->dict[str,Any]:
 api=os.environ.get("CODEX_API_KEY","").strip();binary=_binary()
 if not api:raise RuntimeError("CODEX_API_KEY is not configured")
 if not binary:raise RuntimeError("Codex CLI binary is not installed")
 if payload.get("skill_name")!=PLUGIN_KEY or payload.get("plugin_id")!=PLUGIN_ID:raise RuntimeError("P0 identity mismatch")
 if payload.get("skill_source_path")!=SKILL_RELATIVE_PATH.as_posix():raise RuntimeError("P0 skill path mismatch")
 request=payload.get("request")
 if not isinstance(request,str) or len(request)<40 or len(request)>6000:raise RuntimeError("P0 request must be bounded")
 skill=_resolve_skill(workspace,payload["skill_source_path"]);schema=_load_schema(workspace);manifest=_manifest(workspace);commit=_source_commit(workspace)
 skill_hash=sha256_file(skill);schema_hash=sha256_bytes(canonical_json(schema).encode());request_hash=sha256_bytes(request.encode())
 prompt=f"$skill-analyzer\n\n{request}\n\nReturn only the JSON object required by the supplied output schema."
 with tempfile.TemporaryDirectory(prefix="hso-codex-run-") as t:
  root=Path(t);home=root/"home";tmp=root/"tmp";home.mkdir(mode=0o700);tmp.mkdir(mode=0o700)
  codex_home=root/"codex-home";_write_config(codex_home)
  schema_path=root/"schema.json";final_path=root/"final.json"
  schema_path.write_text(json.dumps(schema,indent=2),encoding="utf-8")
  env=_base_env(codex_home,home,tmp,api)
  links=[];created=[]
  try:
   _,links,created=_register_skills(workspace)
   version=_codex_version(binary,env);_codex_help(binary,env)
   cmd=[binary,"exec","--model",CODEX_MODEL,"--json","--ephemeral","--sandbox","read-only",
        "--ask-for-approval","never","--output-schema",str(schema_path),"--output-last-message",str(final_path),prompt]
   result=subprocess.run(cmd,capture_output=True,text=True,timeout=300,env=env,cwd=str(workspace))
   if result.returncode:raise RuntimeError(f"Codex CLI exited with status {result.returncode}; stderr is not persisted")
   event_receipt=_events(result.stdout or "")
   if not final_path.is_file():raise RuntimeError("Codex did not write final response")
   final=final_path.read_text(encoding="utf-8").strip()
  finally:_cleanup_links(links,created)
 if not final or len(final)>MAX_OUTPUT_CHARS:raise RuntimeError("Codex output empty or exceeded output limit")
 try:analysis=json.loads(final)
 except json.JSONDecodeError as e:raise RuntimeError("Codex final message is not JSON") from e
 if not isinstance(analysis,dict):raise RuntimeError("Codex final message must be a JSON object")
 Draft202012Validator(schema).validate(analysis)
 receipt={
  "receipt_schema_version":"1.0.0","invocation_id":"INV-"+uuid.uuid4().hex,"case_id":analysis["case_id"],
  "status":"SUCCEEDED","timestamp":utc_now(),"host":"openai-codex-cli-exec",
  "codex_cli_version":version,"model":CODEX_MODEL,
  "plugin":{"plugin_id":PLUGIN_ID,"plugin_key":PLUGIN_KEY,"source_repository":SOURCE_REPOSITORY,
   "source_commit":commit,"source_version":manifest["version"],"skill_path":SKILL_RELATIVE_PATH.as_posix(),"skill_sha256":skill_hash},
  "dispatch":{"protocol_method":"codex exec","skill_marker":"$skill-analyzer","skill_reference_supplied":True,
   "skill_discovery_path":".agents/skills/skill-analyzer","skill_directory_registered":True,
   "skill_source_pin_verified":True,"skill_load_attestation":"NO_DEDICATED_CLI_EVENT_EXPOSED",
   "output_schema_sha256":schema_hash,"sandbox":"read-only","approval_policy":"never",
   "sandbox_child_process_network":"disabled_by_codex_read_only_sandbox","thread_ephemeral":True,"jsonl_events":True},
  "session":event_receipt,"usage":event_receipt.get("usage",{}),
  "acceptance":{"output_schema_valid":True,"skill_source_pin_verified":True,"skill_directory_registered":True,
   "skill_reference_supplied":"$skill-analyzer","skill_load_attestation":"NO_DEDICATED_CLI_EVENT_EXPOSED",
   "output_sha256":sha256_bytes(final.encode()),"output_chars":len(final)},
  "request_sha256":request_hash,
  "approval":{"basis":"HMAC_SIGNED_MANUAL_WORKFLOW_DISPATCH","approver":(payload.get("approval_receipt") or {}).get("approver"),
   "nonce":(payload.get("approval_receipt") or {}).get("nonce")}
 }
 artifact=json.dumps({"invocation_receipt":receipt,"analysis_result":analysis},ensure_ascii=False,indent=2)+"\n"
 target,digest=_safe_write(workspace,target_path,artifact)
 return {"target_path":str(target.relative_to(workspace.resolve())),"sha256":digest,"created":True,"no_op":False,
  "thread_id":event_receipt["thread_id"],"turn_id":event_receipt["turn_id"],"host":"openai-codex-cli-exec",
  "source_commit":commit,"skill_sha256":skill_hash,"cli_version":version,"model":CODEX_MODEL,
  "event_counts":event_receipt["event_counts"],"usage":event_receipt.get("usage",{})}
