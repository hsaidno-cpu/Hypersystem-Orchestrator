"use client";
import { FormEvent, useState } from "react";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function LoginForm() {
  const [email,setEmail] = useState(""); const [busy,setBusy] = useState(false); const [message,setMessage] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage("");
    try {
      const supabase = createSupabaseBrowserClient();
      const result = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.origin + "/auth/callback" } });
      if (result.error) throw result.error;
      setMessage("Tautan masuk dikirim apabila alamat email diizinkan. Setelah masuk, akun harus terdaftar sebagai anggota HSO.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Tidak dapat mengirim tautan masuk."); }
    finally { setBusy(false); }
  }
  return <form onSubmit={submit}><div className="field"><label htmlFor="email">Email akun HSO</label><input id="email" type="email" autoComplete="email" required value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="nama@domain.com"/></div><button className="button" type="submit" disabled={busy || !email.trim()}>{busy?"Mengirim...":"Kirim magic link"}</button>{message?<p className="status-message" role="status">{message}</p>:null}</form>;
}
