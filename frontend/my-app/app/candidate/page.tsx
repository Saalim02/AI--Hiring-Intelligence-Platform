"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import AuthWall from "../../src/components/auth-wall";
import { useAuth } from "../../src/hooks/use-auth";
import { apiErrorMessage, listCandidateResumes, Resume, uploadResume } from "../../src/services/api";

export default function CandidateDashboard() {
  const { status, user, logout } = useAuth(); const router = useRouter(); const [resumes, setResumes] = useState<Resume[]>([]); const [error, setError] = useState(""); const [busy, setBusy] = useState(false); const [progress, setProgress] = useState<number | null>(null); const [loading, setLoading] = useState(true);
  useEffect(() => { if (user?.role === "recruiter") router.replace("/"); }, [router, user]);
  const loadResumes = useCallback(async () => { setLoading(true); try { setResumes(await listCandidateResumes()); } catch (err) { setError(apiErrorMessage(err)); } finally { setLoading(false); } }, []);
  useEffect(() => { if (status === "authenticated" && user?.role === "candidate") queueMicrotask(() => void loadResumes()); }, [loadResumes, status, user]);
  if (status !== "authenticated") return <AuthWall />;
  const onUpload = async (file?: File) => { if (!file) return; if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) { setError("Upload a PDF resume."); return; } if (file.size > 10 * 1024 * 1024) { setError("Keep resume files under 10 MB."); return; } setBusy(true); setProgress(0); setError(""); try { await uploadResume(file, setProgress); await loadResumes(); } catch (err) { setError(apiErrorMessage(err)); } finally { setBusy(false); setProgress(null); } };
  if (user?.role !== "candidate") return <AuthWall />;
  return <main className="auth-wall"><section className="auth-card"><div className="topbar"><div><p className="eyebrow">Candidate workspace</p><h1>Welcome, {user.username}</h1></div><div className="button-row"><Link className="button secondary" href="/profile">My profile</Link><button className="text-link sign-out" type="button" onClick={logout}>Sign out</button></div></div>{error && <div className="notice error" role="alert">{error}</div>}<p className="muted">Your account and uploaded resumes are private to you. Recruiter screening is handled only through authorized recruiter workspaces.</p><div className="stats-grid"><div className="panel stat"><p className="eyebrow">Your resumes</p><strong>{resumes.length}</strong><p className="muted">Uploaded to your account</p></div><div className="panel stat"><p className="eyebrow">Account role</p><strong>Candidate</strong><p className="muted">Personal workspace</p></div></div><label className="button primary full">{busy ? `Uploading${progress !== null ? ` ${progress}%` : "…"}` : "Upload your resume"}<input hidden type="file" accept="application/pdf,.pdf" disabled={busy} onChange={(event) => void onUpload(event.target.files?.[0])} /></label><h2>Your resumes</h2>{loading ? <div className="state" role="status">Loading your resumes…</div> : resumes.length === 0 ? <div className="state">No resume uploaded yet.</div> : resumes.map((resume) => <Link className="candidate-row" href={`/candidates/${resume.id}`} key={resume.id}><span className="candidate-avatar">{resume.filename.slice(0, 1).toUpperCase()}</span><span className="candidate-main"><strong>{resume.filename}</strong><span className="muted">{resume.skills || "Skills are being processed"}</span></span></Link>)}</section></main>;
}
