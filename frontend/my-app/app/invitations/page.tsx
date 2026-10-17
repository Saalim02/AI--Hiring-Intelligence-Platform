"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import AuthWall from "../../src/components/auth-wall";
import AutomaticInvitations from "../../src/components/automatic-invitations";
import { apiErrorMessage, listResumes, Resume } from "../../src/services/api";
import { useAuth } from "../../src/hooks/use-auth";

export default function InvitationsPage() {
  const { status, user } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [error, setError] = useState("");
  const load = useCallback(async () => { try { setResumes(await listResumes()); } catch (err) { setError(apiErrorMessage(err)); } }, []);
  useEffect(() => { if (status === "authenticated" && user?.role === "recruiter") queueMicrotask(() => void load()); }, [load, status, user]);
  if (status !== "authenticated" || user?.role !== "recruiter") return <AuthWall />;
  return <main className="auth-wall"><section className="auth-card" style={{ maxWidth: "1200px" }}><div className="topbar"><div><p className="eyebrow">Recruiter workspace</p><h1>Automatic invitations</h1></div><Link className="button secondary" href="/">Back to screening</Link></div>{error && <div className="notice error" role="alert">{error}</div>}<AutomaticInvitations resumes={resumes} /></section></main>;
}
