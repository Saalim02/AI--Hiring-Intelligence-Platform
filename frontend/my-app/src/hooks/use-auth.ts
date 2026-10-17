"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken, getCurrentUser, setAccessToken, User } from "../services/api";

export type AuthStatus = "checking" | "authenticated" | "unauthenticated";

export function useAuth() {
  const [status, setStatus] = useState<AuthStatus>("checking");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const refresh = async () => {
      if (!getAccessToken()) { setUser(null); setStatus("unauthenticated"); return; }
      try { setUser(await getCurrentUser()); setStatus("authenticated"); } catch { setUser(null); setStatus("unauthenticated"); }
    };
    window.addEventListener("resume-auth-change", refresh);
    void refresh();
    return () => window.removeEventListener("resume-auth-change", refresh);
  }, []);

  const logout = useCallback(() => {
    setAccessToken(null);
    setStatus("unauthenticated");
  }, []);

  return { status, user, logout };
}
