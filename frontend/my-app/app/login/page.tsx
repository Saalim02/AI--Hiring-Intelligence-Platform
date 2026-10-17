"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import api, { apiErrorMessage, setAccessToken } from "../../src/services/api";

export default function LoginPage() {
  const router = useRouter(); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => { event.preventDefault(); setBusy(true); setError(""); try { const body = new URLSearchParams({ username: email, password }); const { data } = await api.post<{ access_token: string; user: { role: "recruiter" | "candidate" } }>("/auth/login", body, { headers: { "Content-Type": "application/x-www-form-urlencoded" } }); setAccessToken(data.access_token); router.replace(data.user.role === "candidate" ? "/candidate" : "/"); } catch (err) { setError(apiErrorMessage(err)); } finally { setBusy(false); } };
  return <main className="auth-wall"><form className="auth-card" onSubmit={submit}><Link className="brand" href="/"><span className="brand-mark">H</span><span>hirewise</span></Link><p className="eyebrow">Welcome back</p><h1>Sign in to your workspace</h1>{error && <div className="notice error" role="alert">{error}</div>}<label className="field-label" htmlFor="email">Email</label><input id="email" type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" /><label className="field-label" htmlFor="password">Password</label><input id="password" type="password" required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Your password" /><button className="button primary full" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button><p className="auth-switch muted">New to hirewise? <Link href="/signup">Create an account</Link></p></form></main>;
}
