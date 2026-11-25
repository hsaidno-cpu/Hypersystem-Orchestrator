import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

type Props={params:Promise<{id:string}>};
type Row=Record<string,any>;
function dateLabel(value?:string|null) {
  if(!value)return "Belum tersedia";
  const d=new Date(value);return Number.isNaN(d.getTime())?value:new Intl.DateTimeFormat("id-ID",{dateStyle:"medium",timeStyle:"short",timeZone:"Asia/Makassar"}).format(d);
}
function Pill({value}:{value?:string|null}) {
  const v=String(value??"UNKNOWN").toLowerCase();
  const tone=["pass","verified","accepted","succeeded"].includes(v)?"good":["blocked","hold","pending","unknown","not_run"].includes(v)?"warn":["fail","failed","critical"].includes(v)?"bad":"";
  return <span className={"pill "+tone}>{String(value??"UNKNOWN").replaceAll("_"," ").toUpperCase()}</span>;
}
export default async function TaskDetail({params}:Props) {
  const {id}=await params;
  const supabase=await createSupabaseServerClient();
  const {data:userData}=await supabase.auth.getUser();
  if(!userData.user)redirect("/login");
  const {data:member}=await supabase.from("hso_members").select("active,role").eq("user_id",userData.user.id).maybeSingle();
  if(!member?.active)redirect("/");
  const {data:item}=await supabase.from("hso_work_items").select("*").eq("id",id).maybeSingle();
  if(!item)notFound();
  const [historyQ,execQ,evidenceQ,verifiedQ]=await Promise.all([
    supabase.from("hso_work_item_history").select("*").eq("work_item_id",id).order("changed_at",{ascending:false}).limit(50),
    supabase.from("hso_executions").select("*").eq("related_work_item",item.external_id).order("observed_at",{ascending:false}).limit(20),
    supabase.from("hso_evidence_records").select("*").eq("related_work_item",item.external_id).order("observed_at",{ascending:false}).limit(30),
    supabase.from("hso_verified_work_items_v").select("verified_completion").eq("id",id).maybeSingle()
  ]);
  const history=(historyQ.data??[]) as Row[];
  const executions=(execQ.data??[]) as Row[];
  const evidence=(evidenceQ.data??[]) as Row[];
  const files=executions.flatMap(x=>Array.isArray(x.changed_files)?x.changed_files:[]);
  return <main className="shell">
    <header className="topbar"><div><div className="eyebrow">HSO Mission Control · Work Item</div><h1>{item.title}</h1><div className="subtitle">{item.item_key?"HSO-"+String(item.item_key).padStart(3,"0"):item.external_id}</div></div><Link href="/" className="button secondary">← Back to Mission Control</Link></header>
    <section className="panel"><div className="panel-heading"><h3>Execution state vs verification state</h3><Pill value={verifiedQ.data?.verified_completion===true?"VERIFIED":"NOT VERIFIED"}/></div>
      <div className="detail-state-grid"><div><small>Execution</small><Pill value={item.execution_state}/></div><div><small>Verification</small><Pill value={item.verification_state}/></div><div><small>Gate</small><Pill value={item.gate_state}/></div><div><small>Approval</small><Pill value={item.approval_state??"UNSET"}/></div><div><small>Security</small><Pill value={item.security_disposition??"UNSET"}/></div><div><small>Priority</small><Pill value={item.priority}/></div></div>
    </section>
    <div className="two-col">
      <section className="panel"><h3>Scope & objective</h3><p>{item.next_action??"Next action has not been specified."}</p><h4>Acceptance criteria</h4><p>{item.acceptance_criteria??"No acceptance criteria recorded."}</p><h4>Blocker / risk</h4><p>{item.blocker??"No blocker recorded."}</p><h4>Dependencies</h4><pre className="prompt-text">{JSON.stringify({narrative:item.dependencies,work_item_ids:item.dependency_work_item_ids},null,2)}</pre></section>
      <section className="panel"><h3>Source & target</h3><dl className="detail-list">
        <dt>Source instruction</dt><dd>{item.source_url?<a href={item.source_url} target="_blank" rel="noreferrer">{item.source_url}</a>:"Not available"}</dd>
        <dt>Project area / stage</dt><dd>{item.project_area??"—"} · {item.ecosystem_stage??"—"}</dd>
        <dt>Parent milestone</dt><dd>{item.parent_milestone_id??"Not linked"}</dd>
        <dt>Change surface</dt><dd>{item.change_surface??"Not set"} · target {item.execution_target??"Not set"}</dd>
        <dt>Branch</dt><dd><span className="mono">{item.target_branch??"Not identified"}</span></dd>
        <dt>Head SHA</dt><dd><span className="mono">{item.head_commit_sha??"Not identified"}</span></dd>
        <dt>Reviewed SHA</dt><dd><span className="mono">{item.reviewed_commit_sha??"Not recorded"}</span></dd>
        <dt>CI SHA</dt><dd><span className="mono">{item.ci_commit_sha??"Not recorded"}</span></dd>
        <dt>PR</dt><dd>{item.pr_url?<a href={item.pr_url} target="_blank" rel="noreferrer">{item.pr_url}</a>:"Not linked"}</dd>
        <dt>CI</dt><dd>{item.ci_run_url?<a href={item.ci_run_url} target="_blank" rel="noreferrer">{item.ci_run_url}</a>:"Not linked"}</dd>
      </dl></section>
    </div>
    <div className="section-title"><h2>Execution history & retries</h2><span>{executions.length} linked runs</span></div>
    <section className="panel">{executions.length?executions.map(run=><div className="history-row" key={run.id}>
      <div><strong>{run.run_name}</strong><small>{run.run_type} · {run.executing_agent??run.owner_role??"Agent not recorded"} · {dateLabel(run.completed_at)}</small></div>
      <Pill value={run.status}/><Pill value={run.verification_state}/><span>Retries: {run.retry_count??0}</span>
      {run.target_branch?<small>branch {run.target_branch}</small>:null}
      {run.head_commit_sha?<small className="mono">{run.head_commit_sha}</small>:null}
      {run.github_workflow_url?<a href={run.github_workflow_url} target="_blank" rel="noreferrer">Workflow ↗</a>:null}
      {run.execution_receipt_url?<a href={run.execution_receipt_url} target="_blank" rel="noreferrer">Receipt ↗</a>:null}
      {run.validation_summary?<p>{run.validation_summary}</p>:null}
      {run.acceptance_result?<Pill value={run.acceptance_result}/>:null}
      {run.stop_reason?<p className="small">Stop: {run.stop_reason}</p>:null}
      {Array.isArray(run.changed_files)&&run.changed_files.length?<ul>{run.changed_files.map((f:string,i:number)=><li key={i} className="mono">{f}</li>)}</ul>:null}
    </div>):<div className="empty">Belum ada execution record yang terkait langsung dengan task ID ini.</div>}</section>
    <div className="section-title"><h2>Status & gate history</h2><span>{history.length} recorded transitions</span></div>
    <section className="panel">{history.length?history.map(h=><div className="history-row" key={h.id}>
      <div><strong>{dateLabel(h.changed_at)}</strong><small>{h.changed_fields?.join(", ")}</small></div>
      <div>{h.from_execution_state??"—"} → <strong>{h.to_execution_state??"—"}</strong></div>
      <div>{h.from_gate_state??"—"} → <Pill value={h.to_gate_state}/></div>
      {h.source_url?<a href={h.source_url} target="_blank" rel="noreferrer">Source ↗</a>:null}
    </div>):<div className="empty">Belum ada transisi setelah history capture aktif. Riwayat lama tidak direkonstruksi secara fiktif.</div>}</section>
    <div className="section-title"><h2>Acceptance evidence</h2><span>{evidence.length} evidence records</span></div>
    <section className="panel">{evidence.length?evidence.map(ev=><div className="history-row" key={ev.id}>
      <div><strong>{ev.title}</strong><small>{ev.evidence_type} · {ev.verifier_role??"Verifier not recorded"} · {dateLabel(ev.verified_at)}</small></div><Pill value={ev.evidence_state}/><Pill value={ev.freshness}/>
      <div className="mono">SHA {ev.commit_sha??"—"}</div>
      {ev.source_url?<a href={ev.source_url} target="_blank" rel="noreferrer">Evidence ↗</a>:null}
      {ev.known_limitation?<p>{ev.known_limitation}</p>:null}
    </div>):<div className="empty">Evidence belum terkait melalui relation ke work item ini.</div>}</section>
  </main>;
}
