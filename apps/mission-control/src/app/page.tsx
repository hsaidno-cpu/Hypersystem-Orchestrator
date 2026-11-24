import Link from "next/link";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import RefreshButton from "./refresh-button";
import PromptCopy from "./prompt-copy";

type Row = Record<string, any>;
function tone(value?: string | null) {
  const v = String(value ?? "").toLowerCase();
  if (["connected","succeeded","success","pass","verified","accepted","primary_selected","on_track"].includes(v)) return "good";
  if (["degraded","partial","stale","hold","blocked","not_configured","not_assessed","unknown","unmeasured","at_risk","pending"].includes(v)) return "warn";
  if (["failed","failure","fail","critical","source_stale","no_eligible_action"].includes(v)) return "bad";
  return "";
}
function Pill({value}:{value?:string|null}) {
  return <span className={"pill "+tone(value)}>{String(value ?? "UNKNOWN").replaceAll("_"," ").toUpperCase()}</span>;
}
function Metric({label,value,note,kind}:{label:string;value:string|number;note:string;kind?:string}) {
  return <div className={"metric-card " + (kind ?? "")}><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-note">{note}</div></div>;
}
function dateLabel(value?:string|null) {
  if (!value) return "Belum tersedia";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return new Intl.DateTimeFormat("id-ID",{dateStyle:"medium",timeStyle:"short",timeZone:"Asia/Makassar"}).format(d);
}
function percent(value:number|null|undefined) {
  return value === null || value === undefined || !Number.isFinite(Number(value)) ? "Belum terukur" : Number(value).toFixed(1)+"%";
}
function milestoneHealth(row:Row) {
  if (row.failed_count > 0 || row.blocked_count > 0) return "BLOCKED / AT RISK";
  if (row.pending_approval_count > 0) return "PENDING DECISION";
  if (row.measurement_state === "UNMEASURED") return "UNMEASURED";
  if (row.expected_progress_pct !== null && row.expected_progress_pct !== undefined &&
      row.weighted_progress_pct !== null && Number(row.weighted_progress_pct) < Number(row.expected_progress_pct)) return "BEHIND PLAN";
  if (row.weight_coverage_pct < 100) return "PARTIAL COVERAGE";
  return "TRACKING";
}
const severityOrder:Record<string,number> = { CRITICAL:0, HIGH:1, MEDIUM:2, LOW:3, INFO:4 };
function SparkBars({rows}:{rows:Row[]}) {
  const values=rows.filter(x=>x.weighted_progress_pct!==null && x.weighted_progress_pct!==undefined);
  if (!values.length) return <div className="empty">Belum ada tren progres berbobot yang dapat dihitung. Isi Scope Weight dan verifikasi penerimaan terlebih dahulu.</div>;
  return <div className="sparkbars">{values.map((row,i)=>{
    const v=Math.max(2,Math.min(100,Number(row.weighted_progress_pct)));
    return <div className="sparkbar-wrap" key={row.id ?? row.computed_at ?? i} title={dateLabel(row.computed_at)+" · "+percent(v)}>
      <div className="sparkbar" style={{height:v+"%"}} />
      <span>{new Intl.DateTimeFormat("id-ID",{day:"2-digit",month:"2-digit"}).format(new Date(row.computed_at))}</span>
    </div>;
  })}</div>;
}
function PromptPanel({text,taskId}:{text:string;taskId:string}) {
  return <section className="panel prompt-panel">
    <div className="panel-heading"><div><div className="eyebrow">AI execution prompt</div><h3>READY-TO-EXECUTE PROMPT</h3></div><Pill value="snapshot_bound"/></div>
    <p className="muted">Prompt dikompilasi dari Task ID, sumber, branch/commit, evidence, dependensi, otorisasi dan acceptance criteria pada decision run yang sama.</p>
    <pre className="prompt-text">{text}</pre>
    <PromptCopy text={text} />
    <div className="microcopy">Prompt: {taskId} · Jalankan ulang REFRESH & RECOMPUTE jika sumber berubah. Prompt lama tidak otomatis menjadi valid.</div>
  </section>;
}
export default async function Home() {
  const supabase=await createSupabaseServerClient();
  const {data:userData}=await supabase.auth.getUser();
  if (!userData.user) return <main className="auth-wrap"><section className="panel auth-card"><div className="eyebrow">HSO Mission Control</div><h1>Masuk untuk mengendalikan ekosistem.</h1><p className="subtitle">Mission Control menampilkan status berbasis sumber kanonis, bukti dan aturan keputusan.</p><Link className="button" href="/login">Masuk dengan email</Link></section></main>;
  const {data:member}=await supabase.from("hso_members").select("role,active").eq("user_id",userData.user.id).maybeSingle();
  if (!member?.active) return <main className="auth-wrap"><section className="panel auth-card"><div className="eyebrow">Access control</div><h1>Akses belum diberikan.</h1><p className="subtitle">Akun telah terautentikasi, tetapi belum menjadi anggota aktif HSO. Admin perlu mengizinkan user ID di public.hso_members.</p><form action="/api/logout" method="post"><button className="button secondary">Keluar</button></form></section></main>;

  const [sourcesQ,runsQ,itemsQ,execQ,evidenceQ,decisionQ,globalProgressQ,milestoneQ,trendQ,issuesQ,changesQ,historyQ,verifiedQ,criteriaQ,workItemCountQ,activeCountQ,verifiedCountQ,blockerCountQ,criticalCountQ,pendingApprovalCountQ]=await Promise.all([
    supabase.from("hso_sources").select("source_key,display_name,authority_role,status,last_event_at,last_sync_at,last_success_at,freshness_seconds,last_error").order("display_name"),
    supabase.from("hso_sync_runs").select("id,status,trigger_kind,started_at,finished_at,records_seen,records_upserted,error_summary,source_results").order("started_at",{ascending:false}).limit(8),
    supabase.from("hso_work_items").select("id,item_key,title,record_type,project_area,accountable_role,ecosystem_stage,milestone_key,parent_milestone_id,execution_state,verification_state,gate_state,priority,pre_stage,next_action,blocker,dependencies,dependency_work_item_ids,source_url,source_updated_at,scope_weight,weight_rationale,estimated_effort_hours,approval_state,requires_human_approval,security_disposition,execution_risk,change_surface,execution_target,target_branch,head_commit_sha,reviewed_commit_sha,ci_commit_sha,pr_url,ci_run_url,acceptance_criteria,source_verified_at,observed_at").eq("record_type","Work Item").order("observed_at",{ascending:false}).limit(100),
    supabase.from("hso_executions").select("id,run_name,status,owner_role,executing_agent,run_type,source_commit,source_repository,target_branch,head_commit_sha,github_workflow_url,execution_receipt_url,audit_url,changed_files,validation_summary,acceptance_result,stop_reason,retry_count,completed_at,related_work_item,source_url").order("observed_at",{ascending:false}).limit(12),
    supabase.from("hso_evidence_records").select("id,title,evidence_type,evidence_state,freshness,commit_sha,branch_ref,ci_run_url,pr_url,source_url,source_locator,verified_at,verifier_role,known_limitation,related_work_item,payload,observed_at").order("observed_at",{ascending:false}).limit(30),
    supabase.from("hso_decision_runs").select("id,engine_version,policy_version,decision_state,source_health,primary_action,supporting_actions,blocked_actions,pending_decisions,ranking_snapshot,completion_gap,prompt_artifact_id,computed_at").order("computed_at",{ascending:false}).limit(1).maybeSingle(),
    supabase.from("hso_progress_snapshots").select("*").is("milestone_key",null).order("computed_at",{ascending:false}).limit(1).maybeSingle(),
    supabase.from("hso_progress_snapshots").select("*").not("milestone_key","is",null).order("computed_at",{ascending:false}).limit(30),
    supabase.from("hso_progress_snapshots").select("id,milestone_key,weighted_progress_pct,weight_coverage_pct,measurement_state,computed_at").is("milestone_key",null).order("computed_at",{ascending:false}).limit(30),
    supabase.from("hso_issue_records").select("*").eq("verification_state","OPEN").order("detected_at",{ascending:false}).limit(40),
    supabase.from("hso_change_events").select("*").order("event_at",{ascending:false}).limit(12),
    supabase.from("hso_work_item_history").select("id,work_item_id,from_execution_state,to_execution_state,from_gate_state,to_gate_state,changed_at,changed_fields,source_url").order("changed_at",{ascending:false}).limit(20),
    supabase.from("hso_verified_work_items_v").select("id,verified_completion"),
    supabase.from("hso_completion_criteria").select("id,criterion_key,title,state,required,scope_weight,last_evaluated_at").eq("project_key","hso").eq("required",true).order("criterion_key"),
    supabase.from("hso_work_items").select("id",{count:"exact",head:true}).eq("record_type","Work Item"),
    supabase.from("hso_work_items").select("id",{count:"exact",head:true}).eq("record_type","Work Item").eq("execution_state","In progress"),
    supabase.from("hso_verified_work_items_v").select("id",{count:"exact",head:true}).eq("verified_completion",true),
    supabase.from("hso_issue_records").select("id",{count:"exact",head:true}).eq("verification_state","OPEN"),
    supabase.from("hso_issue_records").select("id",{count:"exact",head:true}).eq("verification_state","OPEN").eq("severity","CRITICAL"),
    supabase.from("hso_work_items").select("id",{count:"exact",head:true}).eq("record_type","Work Item").or("approval_state.eq.PENDING,and(requires_human_approval.eq.true,approval_state.neq.APPROVED)")
  ]);
  const sources=(sourcesQ.data??[]) as Row[],runs=(runsQ.data??[]) as Row[],items=(itemsQ.data??[]) as Row[];
  const executions=(execQ.data??[]) as Row[],evidence=(evidenceQ.data??[]) as Row[];
  const decision=decisionQ.data as Row|null,globalProgress=globalProgressQ.data as Row|null;
  const milestoneRaw=(milestoneQ.data??[]) as Row[];
  const milestoneMap=new Map<string,Row>();
  for(const row of milestoneRaw) if(row.milestone_key && !milestoneMap.has(String(row.milestone_key))) milestoneMap.set(String(row.milestone_key),row);
  const milestones=[...milestoneMap.values()];
  const trend=((trendQ.data??[]) as Row[]).reverse();
  const issues=(issuesQ.data??[]) as Row[],changes=(changesQ.data??[]) as Row[],history=(historyQ.data??[]) as Row[];
  const verifiedRows=(verifiedQ.data??[]) as Row[],criteria=(criteriaQ.data??[]) as Row[];
  const verifiedIds=new Set(verifiedRows.filter(x=>x.verified_completion===true).map(x=>x.id));
  const totalWorkItems=workItemCountQ.count??0;
  const verifiedCount=verifiedCountQ.count??verifiedIds.size;
  const activeCount=activeCountQ.count??items.filter(x=>x.execution_state==="In progress").length;
  const openBlockers=blockerCountQ.count??issues.length;
  const criticalCount=criticalCountQ.count??issues.filter(x=>x.severity==="CRITICAL").length;
  const pendingApprovals=pendingApprovalCountQ.count??items.filter(x=>x.approval_state==="PENDING" || (x.requires_human_approval===true && x.approval_state!=="APPROVED")).length;
  const connected=sources.filter(x=>x.status==="connected").length;
  const latest=decision;
  const primary=latest?.primary_action as Row|null;
  const blockedActionRows=(latest?.blocked_actions??[]) as Row[];
  const pendingDecisionRows=(latest?.pending_decisions??[]) as Row[];
  const promptQ=latest?.id
    ? await supabase.from("hso_prompt_artifacts").select("id,prompt_text,prompt_state,task_key,context_hash,created_at").eq("created_from_decision_run",latest.id).order("created_at",{ascending:false}).limit(1).maybeSingle()
    : {data:null,error:null};
  const latestPrompt=promptQ.data as Row|null;
  const executionSuccess=executions.filter(x=>["SUCCEEDED","SUCCESS","PASS"].includes(String(x.status).toUpperCase())).length;
  const executionFailure=executions.filter(x=>["FAILED","FAILURE","FAIL"].includes(String(x.status).toUpperCase())).length;
  const sourceMissing=Object.entries((latest?.source_health??{}) as Row).filter(([key,value])=>!["snapshot_coverage"].includes(key) && !(value as Row)?.fresh);
  const completion=latest?.completion_gap as Row|null;
  const incompleteCriteria=(completion?.incomplete_criteria??[]) as Row[];
  const globalMeasurement=globalProgress?.measurement_state??"UNMEASURED";
  const sortedIssues=[...issues].sort((a,b)=>(severityOrder[String(a.severity)]??9)-(severityOrder[String(b.severity)]??9));
  return <main className="shell">
    <header className="topbar">
      <div className="brand"><div className="brandmark">HSO</div><div><div className="eyebrow">Hypersystem Orchestrator · Decision & Execution Control</div><h1>Mission Control</h1><div className="subtitle">Satu rekomendasi utama. Semua klaim harus punya sumber dan bukti.</div></div></div>
      <div className="actions"><RefreshButton/><form action="/api/logout" method="post"><button className="button secondary">Keluar</button></form></div>
    </header>
    <div className="banner"><strong>Source authority.</strong> GitHub memiliki kode, branch, commit, PR dan CI. Notion memiliki governance, roadmap, ledger dan evidence index. Supabase menyimpan snapshot operasional serta hasil komputasi. Vercel hanya meng-host dashboard. Tidak ada auto-approval, auto-merge, atau auto-release.</div>

    <div className="section-title"><h2>Operational health</h2><span>Last recompute: {dateLabel(latest?.computed_at)}</span></div>
    <section className="grid grid-seven">
      <Metric label="Verified completion" value={verifiedCount+"/"+items.length} note="Status + PASS gate + fresh acceptance evidence" kind="metric-good"/>
      <Metric label="Active work items" value={activeCount} note="Status In progress pada Roadmap"/>
      <Metric label="Open blockers" value={openBlockers} note="Root-cause issues + blocked/hold/fail gates"/>
      <Metric label="Critical issues" value={criticalCount} note="Severity CRITICAL, status OPEN"/>
      <Metric label="Pending approvals" value={pendingApprovals} note="Keputusan manusia yang belum selesai"/>
      <Metric label="Milestone health" value={milestones.filter(x=>x.blocked_count>0||x.failed_count>0).length+" at risk"} note={milestones.length+" group milestone/stage terukur"}/>
      <Metric label="Source freshness" value={connected+"/"+sources.length} note="Sumber berhasil direkonsiliasi sesuai SLA"/>
    </section>
    <div className="metric-disclaimer">Progress berbobot: {percent(globalProgress?.weighted_progress_pct)} · coverage bobot {percent(globalProgress?.weight_coverage_pct)} · measurement {String(globalMeasurement).replaceAll("_"," ")}. Task tanpa Scope Weight tidak masuk denominator; Completed tidak dihitung Verified tanpa bukti penerimaan.</div>

    <div className="section-title"><h2>NEXT STRATEGIC ACTION</h2><span><Pill value={latest?.decision_state??"NOT_COMPUTED"}/></span></div>
    {primary && latest?.decision_state==="PRIMARY_SELECTED" ? <section className="panel next-action">
      <div className="action-kicker">PRIMARY NEXT ACTION</div>
      <h2>{primary.title}</h2>
      <div className="primary-meta"><strong>{primary.task_id}</strong><span>Priority score {Number(primary.score??0).toFixed(2)} / 100</span>{primary.source_url?<a href={primary.source_url} target="_blank" rel="noreferrer">Buka sumber kanonis ↗</a>:null}</div>
      <div className="two-col action-details">
        <div><h4>Alasan tindakan direkomendasikan</h4><ul>{(primary.reasons??[]).map((x:string,i:number)=><li key={i}>{x}</li>)}</ul><h4>Prerequisites</h4>
          {(primary.prerequisites??[]).length?<ul>{primary.prerequisites.map((x:Row,i:number)=><li key={i}>{x.task_id}: {x.title} · {x.state}</li>)}</ul>:<div className="muted">Tidak ada dependency terstruktur tambahan.</div>}
        </div>
        <div><h4>Expected outcome</h4><p>{primary.expected_outcome??"Kriteria penerimaan belum dicatat pada sumber roadmap."}</p><h4>Priority breakdown</h4><div className="score-breakdown">{Object.entries(primary.score_breakdown??{}).map(([key,value]:[string,any])=><div key={key}><span>{key.replaceAll("_"," ")}</span><strong>{value.value} × {Math.round(value.weight*100)}%</strong></div>)}</div></div>
      </div>
      {latestPrompt?.prompt_text?<PromptPanel text={latestPrompt.prompt_text} taskId={String(latestPrompt.task_key??primary.task_id)}/>:<div className="empty">Prompt belum dibuat untuk decision run ini. Jalankan REFRESH & RECOMPUTE setelah integrasi dan hard gates tersedia.</div>}
      <div className="two-col followup-actions">
        <div><h4>Supporting actions</h4>{(latest?.supporting_actions??[]).length?<ul>{latest.supporting_actions.map((x:Row,i:number)=><li key={i}><strong>{x.task_id}</strong> · {x.title} <span className="muted">score {Number(x.score).toFixed(1)}</span></li>)}</ul>:<div className="empty">Tidak ada supporting action yang lolos gate.</div>}</div>
        <div><h4>Blocked actions & dependency gaps</h4>{blockedActionRows.length?<ul>{blockedActionRows.slice(0,8).map((x:Row,i:number)=><li key={i}><strong>{x.task_id}</strong> · {x.reasons.join(", ")}</li>)}</ul>:<div className="empty">Tidak ada blocked action yang tercatat.</div>}</div>
      </div>
    </section>:<section className="panel no-action">
      <div className="action-kicker">NO ELIGIBLE ACTION</div>
      <h2>Belum ada pekerjaan yang aman direkomendasikan.</h2>
      <p>Engine tidak akan memilih pekerjaan hanya karena terlihat mendesak. Periksa sumber kedaluwarsa, bukti, dependency ID, commit, CI, approval, dan input bobot prioritas yang belum lengkap.</p>
      <div className="source-alerts">{sourceMissing.slice(0,5).map(([key,value])=><div key={key}><strong>{key}</strong><Pill value={(value as Row)?.status}/><span>{(value as Row)?.last_error??"Freshness SLA tidak terpenuhi."}</span></div>)}</div>
      <div className="blocked-summary"><strong>{blockedActionRows.length} pekerjaan terblokir oleh hard gate</strong><strong>{pendingDecisionRows.length} keputusan menunggu manusia</strong></div>
      {blockedActionRows.length?<ul className="compact-list">{blockedActionRows.slice(0,12).map((x:Row,i:number)=><li key={i}><strong>{x.task_id} · {x.title}</strong><div className="microcopy">{x.reasons.join(" · ")}</div></li>)}</ul>:null}
      <p className="muted">Decision state: {latest?.decision_state??"BELUM DIHITUNG"} · {dateLabel(latest?.computed_at)}</p>
    </section>}

    <div className="section-title"><h2>Project Progress Analytics</h2><span>Weighted scope + verified acceptance</span></div>
    <div className="two-col analytics-grid">
      <section className="panel"><div className="panel-heading"><h3>Progress trend</h3><span>{trend.filter(x=>x.weighted_progress_pct!==null).length} measured points</span></div><SparkBars rows={trend}/><div className="microcopy">Hanya snapshot dengan bobot terisi dan verified evidence yang tampil sebagai persentase. Jumlah checklist tidak menjadi pembagi.</div></section>
      <section className="panel"><div className="panel-heading"><h3>Execution health</h3><span>12 execution terakhir</span></div><div className="execution-health"><div><strong>{executionSuccess}</strong><span>Success</span></div><div><strong>{executionFailure}</strong><span>Failure</span></div><div><strong>{executions.filter(x=>String(x.status).toUpperCase()==="BLOCKED").length}</strong><span>Blocked</span></div><div><strong>{executions.filter(x=>String(x.verification_state).toUpperCase()==="PASS").length}</strong><span>Verified</span></div></div><div className="microcopy">Run yang sukses tidak otomatis membuktikan acceptance atau deployment.</div></section>
    </div>
    <section className="panel"><div className="panel-heading"><h3>Milestone & ecosystem-stage progress</h3><span>Actual weighted progress vs planned baseline</span></div>
      {milestones.length?<div className="milestone-list">{milestones.map(row=><div className="milestone-row" key={row.id}>
        <div className="milestone-title"><strong>{row.milestone_title??row.milestone_key}</strong><small>{row.group_type} · {row.verified_count}/{row.total_work_items} verified · coverage {percent(row.weight_coverage_pct)}</small><small>Baseline {row.baseline_start_date??"—"} · target {row.target_date??"—"}</small></div>
        <div className="progress-track"><div className="progress-fill" style={{width:(row.weighted_progress_pct??0)+"%"}}/></div>
        <div className="milestone-value">{percent(row.weighted_progress_pct)}<small>{row.expected_progress_pct===null||row.expected_progress_pct===undefined?"Target belum ditetapkan":"vs "+percent(row.expected_progress_pct)}</small></div><Pill value={milestoneHealth(row)}/>
      </div>)}</div>:<div className="empty">Belum ada snapshot milestone. Data akan muncul setelah rekonsiliasi berhasil.</div>}
    </section>

    <div className="section-title"><h2>Workflow Execution Tracker</h2><span>{items.length} displayed · {totalWorkItems} total work items</span></div>
    <section className="panel table-wrap"><table><thead><tr><th>Task ID / Work item</th><th>Status</th><th>Verification</th><th>Gate</th><th>Priority</th><th>Scope weight</th><th>Approval</th><th>Milestone / Stage</th><th>Dependencies</th><th>Source</th></tr></thead>
      <tbody>{items.map(item=><tr key={item.id}>
        <td><Link href={"/tasks/"+item.id}>{item.item_key?"HSO-"+String(item.item_key).padStart(3,"0"):item.id.slice(0,8)} · {item.title}</Link><div className="microcopy">{item.accountable_role??item.project_area??"Owner/source role in Notion"}</div></td>
        <td><Pill value={item.execution_state}/></td><td><Pill value={verifiedIds.has(item.id)?"VERIFIED":item.verification_state??"NOT_VERIFIED"}/></td>
        <td><Pill value={item.gate_state}/></td><td><Pill value={item.priority}/></td><td>{item.scope_weight??"Unweighted"}</td><td><Pill value={item.approval_state??"UNSET"}/></td><td>{item.parent_milestone_id?"Milestone "+item.parent_milestone_id:item.ecosystem_stage??"Unassigned"}</td>
        <td>{(item.dependency_work_item_ids??[]).length?item.dependency_work_item_ids.join(", "):item.dependencies?"Narrative dependency; ID mapping required":"—"}</td>
        <td>{item.source_url?<a href={item.source_url} target="_blank" rel="noreferrer">Notion ↗</a>:"Not available"}</td>
      </tr>)}</tbody></table>
      {!items.length?<div className="empty">Roadmap belum tersinkronkan ke Supabase.</div>:null}
    </section>

    <div className="section-title"><h2>Blockers, Errors & Diagnostics</h2><span>Root-cause grouped</span></div>
    <section className="panel">{issues.length?<div className="issue-list">{sortedIssues.slice(0,12).map(issue=><div className="issue-row" key={issue.id}>
      <div className="issue-severity"><Pill value={issue.severity}/><small>{issue.issue_type}</small></div>
      <div className="issue-content"><strong>{issue.root_cause_key}</strong><p>{issue.root_cause??issue.message}</p><small>{issue.occurrence_count??(issue.affected_work_items??[]).length} impacted task(s) · {issue.affected_work_items?.join(", ")}</small><small>Impact: {issue.impact??"Belum dianalisis"} </small><small>Resolution: {issue.resolution??"Belum dicatat"} · verification {issue.verification_state}</small></div>
      <div className="issue-location">{issue.location??"Location unknown"}</div>
    </div>)}</div>:<div className="empty">Tidak ada issue terbuka yang tercatat pada snapshot saat ini.</div>}</section>

    <div className="section-title"><h2>Pending decisions & completion gap</h2><span>Project Completion Intelligence</span></div>
    <div className="two-col">
      <section className="panel"><h3>Pending approvals</h3>{pendingDecisionRows.length?<ul className="compact-list">{pendingDecisionRows.map((x:Row,i:number)=><li key={i}><strong>{x.task_id} · {x.title}</strong><Pill value={x.approval_state}/><div className="microcopy">{x.source_url}</div></li>)}</ul>:<div className="empty">Tidak ada pending approval pada decision run terakhir.</div>}</section>
      <section className="panel"><h3>Required deliverables</h3><div className="completion-summary">{completion?.verified_criteria_count??0} / {completion?.required_criteria_count??0} verified</div>{incompleteCriteria.length?<ul className="compact-list">{incompleteCriteria.slice(0,10).map((x:Row,i:number)=><li key={i}><strong>{x.criterion_key} · {x.title}</strong><Pill value={x.state}/></li>)}</ul>:<div className="empty">Kriteria akhir belum dikonfigurasi, atau seluruh kriteria wajib telah diterima.</div>}</section>
    </div>

    <div className="section-title"><h2>Change Intelligence & Notifications</h2><span>Since last observed source event</span></div>
    <section className="panel">{changes.length?<div className="change-list">{changes.map(change=><div className="change-row" key={change.id}>
      <div><strong>{change.title}</strong><small>{change.provider} · {change.event_type} · {dateLabel(change.event_at)}</small></div>
      <Pill value={change.impact}/><span>{change.follow_up}</span>
      {change.source_url?<a href={change.source_url} target="_blank" rel="noreferrer">Open source ↗</a>:null}
    </div>)}</div>:<div className="empty">Belum ada perubahan masuk pada change event inbox.</div>}</section>

    <div className="section-title"><h2>Source freshness & synchronization</h2><span>Reconciliation, not browser reload</span></div>
    <section className="panel">
      {sources.map(source=>{
        const age=source.last_success_at?Math.max(0,Math.round((Date.now()-new Date(source.last_success_at).getTime())/1000)):null;
        const isFresh=source.status==="connected"&&age!==null&&age<=Number(source.freshness_seconds??1800);
        return <div className="source-row" key={source.source_key}><div><div className="source-name">{source.display_name}</div><div className="source-role">{source.authority_role} · last success {dateLabel(source.last_success_at)} · SLA {source.freshness_seconds??"—"}s</div>{source.last_error?<div className="small">{source.last_error}</div>:null}</div><div className="source-status"><Pill value={isFresh?"FRESH":source.status}/><small>{age===null?"no success":age+"s ago"}</small></div></div>;
      })}
    </section>
    <div className="two-col">
      <section className="panel"><h3>Latest synchronization runs</h3>{runs.length?runs.map(run=><div className="work-row" key={run.id}><div><div className="source-name">{run.trigger_kind} · {run.records_upserted} updated</div><div className="source-role">{dateLabel(run.started_at)} · {run.records_seen} observed</div>{run.error_summary?<div className="small">{run.error_summary}</div>:null}</div><Pill value={run.status}/></div>):<div className="empty">Belum ada sync run. Credential integrasi perlu dikonfigurasi.</div>}</section>
      <section className="panel"><h3>Latest evidence</h3>{evidence.slice(0,8).map(ev=><div className="work-row" key={ev.id}><div><div className="source-name">{ev.source_url?<a href={ev.source_url} target="_blank" rel="noreferrer">{ev.title}</a>:ev.title}</div><div className="source-role">{ev.evidence_type} · SHA <span className="mono">{ev.commit_sha?.slice(0,10)??"—"}</span></div>{ev.known_limitation?<div className="small">{ev.known_limitation}</div>:null}</div><Pill value={ev.evidence_state}/></div>)}</section>
    </div>
    <footer className="footer"><span>HSO Mission Control · intelligence v2 · engine {latest?.engine_version??"not computed"} · policy {latest?.policy_version??"not computed"}</span><span>{userData.user.email??userData.user.id} · role {member.role}</span></footer>
  </main>;
}

