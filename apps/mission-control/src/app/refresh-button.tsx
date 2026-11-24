"use client";

import { useState } from "react";

export default function RefreshButton() {
  const [busy,setBusy]=useState(false);
  const [message,setMessage]=useState("");
  async function refresh() {
    setBusy(true); setMessage("");
    try {
      const response=await fetch("/api/refresh",{method:"POST"});
      const body=await response.json();
      if(!response.ok) throw new Error(body.detail || body.error || "Refresh gagal.");
      const engine=body.decision_engine;
      const primary=engine?.primary_action;
      const result=primary?.task_id ? " · Primary action: "+primary.task_id : " · "+(engine?.decision_state ?? "decision engine belum menghitung");
      setMessage("Sync "+body.status+": "+(body.records_upserted??0)+" record diperbarui"+result);
      window.location.reload();
    } catch(error) {
      setMessage(error instanceof Error?error.message:"Refresh & recompute gagal.");
    } finally { setBusy(false); }
  }
  return <div className="refresh-control">
    <button className="button" onClick={refresh} disabled={busy}>{busy?"SYNC + RECOMPUTE...":"↻ REFRESH & RECOMPUTE"}</button>
    {message?<div className="status-message">{message}</div>:null}
  </div>;
}
