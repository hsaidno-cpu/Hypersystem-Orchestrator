import Link from "next/link";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import RefreshButton from "./refresh-button";

type Row = Record<string, any>;
function tone(value?: string | null) {
  const v=(value??"").toLowerCase();
  if(["connected","succeeded","success","pass","verified","accepted"].includes(v)) return "good";
  if(["degraded","partial","stale","hold","blocked","not_configured","not assessed","not_assessed","unknown"].includes(v)) return "warn";
  if(["failed","failure","fail","error"].includes(v)) return "bad";
  return "";
}
function Pill({value}:{value?:string|null}) {
  return <span className={"pill "+tone(value)}>{(value??"UNKNOWN").replaceAll("_"," ").toUpperCase()}</span>;
}
function Metric({label,value,note}:{label:string;value:number|string;note:string}) {
  return <div className="card"><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-note">{note}</div></div>;
}
function dateLabel(value?:string|null) {
  if(!value) return "Belum pernah";
  const date=new Date(value);
  return Number.isNaN(date.getTime())?value:new Intl.DateTimeFormat("id-ID",{dateStyle:"medium",timeStyle:"short",timeZone:"Asia/Makassar"}).format(date);
}
export default async function Home() {
  const supabase=await createSupabaseServerClient();
  const {data:userData}=await supabase.auth.getUser();
  if(!userData.user) return <main className="auth-wrap"><section className="card auth-card"><div className="eyebrow">HSO Mission Control</div><h1>Control plane belum dibuka.</h1><p className="subtitle">Masuk terlebih dahulu untuk melihat status, bukti, dan sinkronisasi ekosistem.</p><Link className="button" href="/login">Masuk dengan email</Link></section></main>;
  const {data:member}=await supabase.from("hso_members").select("role,active").eq("user_id",userData.user.id).maybeSingle();
  if(!member?.active) return <main className="auth-wrap"><section className="card auth-card"><div className="eyebrow">Access control</div><h1>Akses belum diberikan.</h1><p className="subtitle">Autentikasi berhasil, tetapi akun ini belum terdaftar sebagai anggota aktif HSO. Admin harus menambahkan ID pengguna ke <span className="mono">public.hso_members</span>.</p><form action="/api/logout" method="post"><button className="button secondary">Keluar</button></form></section></main>;
  const [sourcesQ,runsQ,itemsQ,execQ,evidenceQ,notifsQ]=await Promise.all([
    supabase.from("hso_sources").select("source_key,display_name,authority_role,status,last_sync_at,last_success_at,last_error").order("display_name"),
    supabase.from("hso_sync_runs").select("id,status,trigger_kind,started_at,finished_at,records_seen,records_upserted,error_summary").order("started_at",{ascending:false}).limit(8),
    supabase.from("hso_work_items").select("id,title,execution_state,gate_state,priority,pre_stage,next_action,source_url,observed_at").order("observed_at",{ascending:false}).limit(12),
    supabase.from("hso_executions").select("id,run_name,status,owner_role,github_workflow_url,completed_at").order("observed_at",{ascending:false}).limit(8),
    supabase.from("hso_evidence_records").select("id,title,evidence_type,evidence_state,freshness,commit_sha,ci_run_url,pr_url,source_url,observed_at").order("observed_at",{ascending:false}).limit(10),
    supabase.from("hso_notifications").select("id,severity,category,message,state,created_at").eq("state","open").order("created_at",{ascending:false}).limit(8)
  ]);
  const sources=(sourcesQ.data??[]) as Row[], runs=(runsQ.data??[]) as Row[], items=(itemsQ.data??[]) as Row[];
  const executions=(execQ.data??[]) as Row[], evidence=(evidenceQ.data??[]) as Row[], notifications=(notifsQ.data??[]) as Row[];
  const connected=sources.filter(x=>x.status==="connected").length;
  const freshEvidence=evidence.filter(x=>x.freshness==="FRESH").length;
  const openBlockers=notifications.length+items.filter(x=>String(x.gate_state).toUpperCase()==="BLOCKED").length;
  return <main className="shell">
    <header className="topbar"><div className="brand"><div className="brandmark">HSO</div><div><div className="eyebrow">Hypersystem Orchestrator · Control plane</div><h1>Mission Control</h1><div className="subtitle">Satu panel observasi. Sumber kebenaran tetap berada pada pemiliknya.</div></div></div><div className="actions"><RefreshButton/><form action="/api/logout" method="post"><button className="button secondary">Keluar</button></form></div></header>
    <div className="banner"><strong>Operating boundary.</strong> GitHub adalah sumber engineering; Notion adalah sumber tata kelola, roadmap, dan evidence index; Supabase menyimpan snapshot operasional; dashboard ini tidak otomatis menyetujui, merge, deploy, atau mengubah keputusan.</div>
    <section className="grid">
      <Metric label="Connected sources" value={connected+"/"+sources.length} note="Sumber yang telah lulus autentikasi dan sync"/>
      <Metric label="Open blockers" value={openBlockers} note="Notifikasi terbuka + gate BLOCKED pada sampel terbaru"/>
      <Metric label="Work items observed" value={items.length} note="12 record terbaru dari roadmap"/>
      <Metric label="Fresh evidence" value={freshEvidence} note="Dari evidence yang dimuat ke panel"/>
    </section>
    <div className="section-title"><h2>Source health</h2><span>Waktu lokal Asia/Makassar · {dateLabel(new Date().toISOString())}</span></div>
    <section className="card">{sources.map(source=><div className="source-row" key={source.source_key}><div><div className="source-name">{source.display_name}</div><div className="source-role">{source.authority_role} · sync terakhir: {dateLabel(source.last_sync_at)}</div>{source.last_error?<div className="small">{source.last_error}</div>:null}</div><Pill value={source.status}/></div>)}</section>
    <div className="two-col">
      <section><div className="section-title"><h2>Latest synchronization runs</h2><span>{runs.length} latest</span></div><div className="card">{runs.length?runs.map(run=><div className="work-row" key={run.id}><div><div className="source-name">{run.trigger_kind} · {run.records_upserted} updated</div><div className="source-role">{dateLabel(run.started_at)} · {run.records_seen} observed</div>{run.error_summary?<div className="small">{run.error_summary}</div>:null}</div><Pill value={run.status}/></div>):<div className="empty">Belum ada sync run. Jalankan setelah secret integrasi dikonfigurasi.</div>}</div></section>
      <section><div className="section-title"><h2>Open alerts</h2><span>{notifications.length} open</span></div><div className="card">{notifications.length?notifications.map(n=><div className="work-row" key={n.id}><div><div className="source-name">{n.category}</div><div className="source-role">{n.message}</div></div><Pill value={n.severity}/></div>):<div className="empty">Tidak ada notifikasi terbuka yang tercatat.</div>}</div></section>
    </div>
    <div className="section-title"><h2>Roadmap work items</h2><span>Observasi terbaru, bukan progres agregat seluruh ekosistem</span></div>
    <section className="card table-wrap">{items.length?<table><thead><tr><th>Work item</th><th>Priority</th><th>Execution</th><th>Gate</th><th>PRE</th><th>Next action</th></tr></thead><tbody>{items.map(item=><tr key={item.id}><td>{item.source_url?<a href={item.source_url} target="_blank" rel="noreferrer">{item.title}</a>:item.title}</td><td><Pill value={item.priority}/></td><td><Pill value={item.execution_state}/></td><td><Pill value={item.gate_state}/></td><td className="mono">{item.pre_stage??"—"}</td><td>{item.next_action??"—"}</td></tr>)}</tbody></table>:<div className="empty">Belum ada work item yang berhasil disinkronkan dari Notion Roadmap.</div>}</section>
    <div className="two-col">
      <section><div className="section-title"><h2>Execution ledger</h2><span>Workflow records</span></div><div className="card">{executions.length?executions.map(ex=><div className="work-row" key={ex.id}><div><div className="source-name">{ex.run_name}</div><div className="source-role">{ex.owner_role??"Owner belum dicatat"} · {dateLabel(ex.completed_at)}</div></div><Pill value={ex.status}/></div>):<div className="empty">Ledger belum tersinkronisasi.</div>}</div></section>
      <section><div className="section-title"><h2>Evidence registry</h2><span>CI, PR, source proof</span></div><div className="card">{evidence.length?evidence.slice(0,8).map(ev=><div className="work-row" key={ev.id}><div><div className="source-name">{ev.source_url?<a href={ev.source_url} target="_blank" rel="noreferrer">{ev.title}</a>:ev.title}</div><div className="source-role">{ev.evidence_type} · <span className="mono">{ev.commit_sha?.slice(0,10)??"no SHA"}</span></div></div><Pill value={ev.evidence_state}/></div>):<div className="empty">Belum ada evidence.</div>}</div></section>
    </div>
    <footer className="footer"><span>HSO Mission Control · foundation v0.1 · fail-closed by default</span><span>{userData.user.email??userData.user.id} · role {member.role}</span></footer>
  </main>;
}
