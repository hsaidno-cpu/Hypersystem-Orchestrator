import Link from "next/link";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import RefreshButton from "./refresh-button";

type Row = Record<string, any>;
const tone=(value?:string|null)=>{
 const v=(value??"").toLowerCase();
 if(["connected","succeeded","success","pass","verified","accepted"].includes(v)) return "good";
 if(["degraded","partial","stale","hold","blocked","not_configured","not_assessed","unknown"].includes(v)) return "warn";
 if(["failed","failure","fail","error"].includes(v)) return "bad";
 return "";
};
function Pill({value}:{value?:string|null}) {
 return <span className={"pill "+tone(value)}>{(value??"UNKNOWN").replaceAll("_"," ").toUpperCase()}</span>;
}
function Metric({label,value,note}:{label:string;value:number|string;note:string}) {
 return <div className="card"><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-note">{note}</div></div>;
}
function dateLabel(value?:string|null) {
 if(!value) return "Belum pernah";
 const date=new Date(value);
 if(Number.isNaN(date.getTime())) return value;
 return new Intl.DateTimeFormat("id-ID",{dateStyle:"medium",timeStyle:"short",timeZone:"Asia/Makassar"}).format(date);
}
export default async function Home() {
 const supabase=await createSupabaseServerClient();
 const {data:userData}=await supabase.auth.getUser();
 if(!userData.user) return <main className="auth-wrap"><section className="card auth-card"><div className="eyebrow">HSO Mission Control</div><h1>Control plane belum dibuka.</h1><p className="subtitle">Masuk terlebih dahulu untuk melihat status, bukti, dan sinkronisasi ekosistem.</p><Link className="button" href="/login">Masuk dengan email</Link></section></main>;
 const {data:member}=await supabase.from("hso_members").select("role,active").eq("user_id",userData.user.id).maybeSingle();
 if(!member?.active) return <main className="auth-wrap"><section className="card auth-card"><div className="eyebrow">Access control</div><h1>Akses belum diberikan.</h1><p className="subtitle">Autentikasi berhasil, tetapi akun ini belum terdaftar sebagai anggota aktif HSO. Admin harus menambahkan ID pengguna ke public.hso_members.</p><form action="/api/logout" method="post"><button className="button secondary">Keluar</button></form></section></main>;
 const [sq,rq,wq,xq,eq,nq]=await Promise.all([
  supabase.from("hso_sources").select("source_key,display_name,authority_role,status,last_sync_at,last_error").order("display_name"),
  supabase.from("hso_sync_runs").select("id,status,trigger_kind,started_at,records_seen,records_upserted,error_summary").order("started_at",{ascending:false}).limit(8),
  supabase.from("hso_work_items").select("id,title,execution_state,gate_state,priority,pre_stage,next_action,source_url,observed_at").order("observed_at",{ascending:false}).limit(12),
  supabase.from("hso_executions").select("id,run_name,status,owner_role,github_workflow_url,completed_at").order("observed_at",{ascending:false}).limit(8),
  supabase.from("hso_evidence_records").select("id,title,evidence_type,evidence_state,freshness,commit_sha,ci_run_url,pr_url,source_url,observed_at").order("observed_at",{ascending:false}).limit(10),
  supabase.from("hso_notifications").select("id,severity,category,message,state,created_at").eq("state","open").order("created_at",{ascending:false}).limit(8)
 ]);
 const sources=(sq.data??[]) as Row[],runs=(rq.data??[]) as Row[],items=(wq.data??[]) as Row[];
 const executions=(xq.data??[]) as Row[],evidence=(eq.data??[]) as Row[],alerts=(nq.data??[]) as Row[];
 const connected=sources.filter(x=>x.status==="connected").length;
 const blockers=alerts.length+items.filter(x=>String(x.gate_state).toUpperCase()==="BLOCKED").length;
 const fresh=evidence.filter(x=>x.freshness==="FRESH").length;
 return <main className="shell">
  <header className="topbar"><div className="brand"><div className="brandmark">HSO</div><div><div className="eyebrow">Hypersystem Orchestrator · Control plane</div><h1>Mission Control</h1><div className="subtitle">Satu panel observasi. Sumber kebenaran tetap berada pada pemiliknya.</div></div></div><div className="actions"><RefreshButton/><form action="/api/logout" method="post"><button className="button secondary">Keluar</button></form></div></header>
  <div className="banner"><strong>Operating boundary.</strong> GitHub adalah sumber engineering; Notion adalah sumber tata kelola, roadmap, dan evidence index; Supabase menyimpan snapshot operasional. Dashboard ini tidak otomatis menyetujui, merge, deploy, atau mengubah keputusan.</div>
  <section className="grid">
   <Metric label="Connected sources" value={connected+"/"+sources.length} note="Sumber yang lulus autentikasi dan sync"/>
   <Metric label="Open blockers" value={blockers} note="Alert terbuka + gate BLOCKED pada sampel"/>
   <Metric label="Work items observed" value={items.length} note="Record roadmap terbaru"/>
   <Metric label="Fresh evidence" value={fresh} note="Evidence segar pada sampel terbaru"/>
  </section>
  <div className="section-title"><h2>Source health</h2><span>Asia/Makassar · {dateLabel(new Date().toISOString())}</span></div>
  <section className="card">{sources.map(s=><div className="source-row" key={s.source_key}><div><div className="source-name">{s.display_name}</div><div className="source-role">{s.authority_role} · sync: {dateLabel(s.last_sync_at)}</div>{s.last_error?<div className="small">{s.last_error}</div>:null}</div><Pill value={s.status}/></div>)}</section>
  <div className="two-col">
   <section><div className="section-title"><h2>Synchronization runs</h2><span>{runs.length} latest</span></div><div className="card">{runs.length?runs.map(r=><div className="work-row" key={r.id}><div><div className="source-name">{r.trigger_kind} · {r.records_upserted} updated</div><div className="source-role">{dateLabel(r.started_at)} · {r.records_seen} observed</div>{r.error_summary?<div className="small">{r.error_summary}</div>:null}</div><Pill value={r.status}/></div>):<div className="empty">Belum ada sync run. Secret integrasi belum dikonfigurasi.</div>}</div></section>
   <section><div className="section-title"><h2>Open alerts</h2><span>{alerts.length} open</span></div><div className="card">{alerts.length?alerts.map(a=><div className="work-row" key={a.id}><div><div className="source-name">{a.category}</div><div className="source-role">{a.message}</div></div><Pill value={a.severity}/></div>):<div className="empty">Belum ada notifikasi terbuka yang tercatat.</div>}</div></section>
  </div>
  <div className="section-title"><h2>Roadmap work items</h2><span>Record observasi, bukan agregat progres seluruh ekosistem</span></div>
  <section className="card table-wrap">{items.length?<table><thead><tr><th>Work item</th><th>Priority</th><th>Execution</th><th>Gate</th><th>PRE</th><th>Next action</th></tr></thead><tbody>{items.map(w=><tr key={w.id}><td>{w.source_url?<a href={w.source_url} target="_blank" rel="noreferrer">{w.title}</a>:w.title}</td><td><Pill value={w.priority}/></td><td><Pill value={w.execution_state}/></td><td><Pill value={w.gate_state}/></td><td className="mono">{w.pre_stage??"—"}</td><td>{w.next_action??"—"}</td></tr>)}</tbody></table>:<div className="empty">Belum ada work item yang berhasil disinkronkan dari Notion Roadmap.</div>}</section>
  <div className="two-col">
   <section><div className="section-title"><h2>Execution ledger</h2><span>Workflow records</span></div><div className="card">{executions.length?executions.map(x=><div className="work-row" key={x.id}><div><div className="source-name">{x.run_name}</div><div className="source-role">{x.owner_role??"Owner belum dicatat"} · {dateLabel(x.completed_at)}</div></div><Pill value={x.status}/></div>):<div className="empty">Ledger belum tersinkronisasi.</div>}</div></section>
   <section><div className="section-title"><h2>Evidence registry</h2><span>CI, PR, source proof</span></div><div className="card">{evidence.length?evidence.slice(0,8).map(e=><div className="work-row" key={e.id}><div><div className="source-name">{e.source_url?<a href={e.source_url} target="_blank" rel="noreferrer">{e.title}</a>:e.title}</div><div className="source-role">{e.evidence_type} · <span className="mono">{e.commit_sha?.slice(0,10)??"no SHA"}</span></div></div><Pill value={e.evidence_state}/></div>):<div className="empty">Belum ada evidence.</div>}</div></section>
  </div>
  <footer className="footer"><span>HSO Mission Control · foundation v0.1 · fail-closed by default</span><span>{userData.user.email??userData.user.id} · role {member.role}</span></footer>
 </main>;
}
