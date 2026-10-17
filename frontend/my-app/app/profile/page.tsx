"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import AuthWall from "../../src/components/auth-wall";
import { useAuth } from "../../src/hooks/use-auth";
import { apiErrorMessage, updateProfile } from "../../src/services/api";

export default function ProfilePage() {
  const { status, user, logout } = useAuth();

  if (status !== "authenticated" || !user) return <AuthWall />;

  return <ProfileForm key={user.id} user={user} logout={logout} />;
}

function ProfileForm({ user, logout }: { user: NonNullable<ReturnType<typeof useAuth>["user"]>; logout: () => void }) {
  const [username, setUsername] = useState(user.username);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmed = username.trim();
    if (!trimmed) { setError("Enter your name."); return; }
    setBusy(true); setError(""); setMessage("");
    try {
      await updateProfile(trimmed);
      setMessage("Profile updated. Sign out and back in if your displayed name does not refresh.");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally { setBusy(false); }
  };

  const home = user.role === "candidate" ? "/candidate" : "/";
  return <main className="shell">
    <aside className="sidebar">
      <Link className="brand" href={home}><span className="brand-mark">H</span><span>hirewise</span></Link>
      <p className="sidebar-label">Account</p>
      <nav className="nav"><Link className="nav-item" href={home}>← <span>Back to workspace</span></Link><Link className="nav-item active" href="/profile">◎ <span>My profile</span></Link></nav>
      <div className="sidebar-foot"><div className="avatar">{user.username.slice(0, 1).toUpperCase()}</div><div><strong>{user.username}</strong><p className="muted">{user.role} account</p></div></div>
    </aside>
    <section className="content">
      <header className="topbar"><div><p className="eyebrow">Account settings</p><h1>My profile</h1><p className="muted">Manage the information attached to your Hirewise account.</p></div><button className="text-link sign-out" type="button" onClick={logout}>Sign out ↗</button></header>
      <div className="detail-grid">
        <section className="panel">
          <p className="eyebrow">Personal details</p><h2>Profile information</h2>
          {error && <div className="notice error" role="alert">{error}</div>}
          {message && <div className="notice success" role="status">{message}</div>}
          <form onSubmit={submit}>
            <label className="field-label" htmlFor="profile-name">Display name</label>
            <input id="profile-name" value={username} onChange={e => setUsername(e.target.value)} minLength={1} maxLength={120} required />
            <label className="field-label" htmlFor="profile-email">Email address</label>
            <input id="profile-email" value={user.email} readOnly />
            <label className="field-label" htmlFor="profile-role">Workspace role</label>
            <input id="profile-role" value={user.role === "candidate" ? "Candidate" : "Recruiter"} readOnly />
            <button className="button primary" type="submit" disabled={busy}>{busy ? "Saving…" : "Save profile"}</button>
          </form>
        </section>
        <section className="panel">
          <p className="eyebrow">Access and privacy</p><h2>Your workspace</h2>
          <p className="muted">{user.role === "candidate" ? "Your candidate workspace lists only resumes associated with your account. Resume access is enforced by the backend." : "Your recruiter workspace lists resumes associated with your account. Candidate records from other recruiter accounts are not included."}</p>
          <Link className="button secondary" href={home}>Return to workspace</Link>
        </section>
      </div>
    </section>
  </main>;
}
