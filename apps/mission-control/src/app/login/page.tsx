import LoginForm from "./login-form";
export default function LoginPage() {
  return <main className="auth-wrap"><section className="card auth-card"><div className="eyebrow">Hypersystem Orchestrator</div><h1>Masuk ke Mission Control</h1><p className="subtitle">Autentikasi email. Akses data dibatasi oleh daftar anggota dan Row Level Security.</p><LoginForm/><p className="status-message">Akun yang belum terdaftar di <span className="mono">public.hso_members</span> tidak memperoleh akses data.</p></section></main>;
}
