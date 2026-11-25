"use client";
import { useState } from "react";
export default function RefreshButton() {
  const [busy,setBusy]=useState(false); const [message,setMessage]=useState("");
  async function refresh() {
    setBusy(true); setMessage("");
    try {
      const response=await fetch("/api/refresh",{method:"POST"}); const body=await response.json();
      if(!response.ok) throw new Error(body.detail || body.error || "Refresh gagal.");
      setMessage("Sync " + body.status + ": " + (body.records_upserted ?? 0) + " record diperbarui.");
      window.location.reload();
    } catch(error) { setMessage(error instanceof Error?error.message:"Refresh gagal."); }
    finally { setBusy(false); }
  }
  return <div><button className="button" onClick={refresh} disabled={busy}>{busy?"Menjalankan sync...":"↻ Refresh sources"}</button>{message?<div className="status-message">{message}</div>:null}</div>;
}
