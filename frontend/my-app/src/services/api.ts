import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "/api",
  timeout: 30_000,
});

export type Resume = { id: number; filename: string; skills: string; extracted_text?: string; candidate_name?: string | null; extracted_email?: string | null };
export type User = { id: number; username: string; email: string; role: "recruiter" | "candidate" };
export type UploadResponse = { message: string; resume_id: number; skills: string[] };
export type ScoreFactor = { key: string; label: string; weight: number; weight_percent: number; contribution: number; explanation: string };
export type Evaluation = { candidate: { id: number; filename: string; name?: string | null; email?: string | null }; overall_score: number | null; score_breakdown: ScoreFactor[]; skills: { matched_mandatory: string[]; matched_preferred: string[]; missing_mandatory: string[]; missing_preferred: string[]; ambiguous: string[]; evidence: { skill: string; status: string; snippet: string | null }[] }; strengths: string[]; gaps: string[]; recommendations: string[]; recommendation: { label: string; code: string; reasons: string[] }; evaluation_complete: boolean; rules: { threshold: number; require_all_mandatory_skills: boolean; mandatory_skills_configured: string[] } };
export type AtsResult = Evaluation & { resume_id: number; filename: string; matched_skills: string[]; missing_skills: string[]; recommendation: string; ai_feedback?: string; improvements?: string[] };
export type Ranking = { rank?: number; resume_id?: number; id?: number; filename?: string; score?: number; ats_score?: number; matched_skills?: string[]; evaluation?: Evaluation; [key: string]: unknown };
export type RankingResponse = { total_candidates: number; rankings: Ranking[] };
export type Invitation = { id: number; resume_id: number; candidate_name?: string | null; recipient_email?: string | null; score_snapshot?: number | null; matched_skills: string[]; missing_skills: string[]; eligible: boolean; eligibility_reason: string; status: string; failure_reason?: string | null; provider_message_id?: string | null; attempts: number; sent_at?: string | null };
export type ScreeningSession = { id: number; job_title: string; job_description: string; minimum_ats_score: number; mandatory_skills: string[]; require_all_mandatory_skills: boolean; automatic_invitations_enabled: boolean; first_batch_approved: boolean; invitations: Invitation[] };

export type ApiError = {
  status?: number;
  message: string;
};

export type HealthResponse = { status: "healthy" };

export function setAccessToken(token: string | null) { if (typeof window === "undefined") return; if (token) sessionStorage.setItem("resume_access_token", token); else sessionStorage.removeItem("resume_access_token"); window.dispatchEvent(new Event("resume-auth-change")); }
export function getAccessToken() { return typeof window === "undefined" ? null : sessionStorage.getItem("resume_access_token"); }

api.interceptors.request.use((config) => { const token = getAccessToken(); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
api.interceptors.response.use((response) => response, (error) => { if (error.response?.status === 401) setAccessToken(null); return Promise.reject(error); });

export function apiErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    if (error.code === "ERR_CANCELED" || axios.isCancel(error)) return "Request canceled.";
    if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") return "The request timed out. Please try again.";
    const status = error.response?.status;
    if (status === 401) return "Your session is invalid or your credentials are incorrect. Please sign in again.";
    if (status === 403) return "You do not have permission to perform this action.";
    if (status === 500) return "The screening service failed while processing this request. Please try again.";
    if (status === 503) return "AI processing is temporarily unavailable. No result was created; please try again later.";
    if (!error.response) return "The screening API is unavailable. Check that the backend is running on port 8001.";
    const detail = error.response?.data?.detail || error.response?.data?.message;
    if (typeof detail === "string") return detail;
    if (status === 404) return "The requested record was not found.";
    if (status === 413) return "The uploaded file is too large.";
    if (status === 415) return "Only valid PDF files are supported.";
    if (status === 422) return "Check the submitted fields and try again.";
    if (status === 429) return "Too many requests. Please wait and try again.";
    if (status && status >= 500) return "The screening service encountered an error. Please try again.";
  }
  return "Something went wrong. Please try again.";
}
export async function checkHealth(signal?: AbortSignal) { return (await api.get<HealthResponse>("/health", { signal })).data; }
export async function listResumes(signal?: AbortSignal) { return (await api.get<Resume[]>("/resume/all", { signal })).data; }
export async function getCurrentUser(signal?: AbortSignal) { return (await api.get<User>("/auth/me", { signal })).data; }
export async function updateProfile(username: string) {
  const user = (await api.patch<User>("/auth/me", { username })).data;
  if (typeof window !== "undefined") window.dispatchEvent(new Event("resume-auth-change"));
  return user;
}
export async function getCandidateProfile(signal?: AbortSignal) { return (await api.get<User>("/candidate/me", { signal })).data; }
export async function listCandidateResumes(signal?: AbortSignal) { return (await api.get<Resume[]>("/candidate/resumes", { signal })).data; }
export async function getResume(id: string | number, signal?: AbortSignal) { return (await api.get<Resume>(`/resume/${id}`, { signal })).data; }
export async function uploadResume(file: File, onUploadProgress?: (progress: number) => void) { const form = new FormData(); form.append("file", file); return (await api.post<UploadResponse>("/resume/upload", form, { onUploadProgress: (event) => { if (event.total) onUploadProgress?.(Math.round((event.loaded / event.total) * 100)); } })).data; }
export async function scoreResume(id: number, jobDescription: string) { return (await api.post<AtsResult>(`/resume/ats-score/${id}`, null, { params: { job_description: jobDescription } })).data; }
export async function searchResumes(query: string, signal?: AbortSignal) { return (await api.get<{ matched_candidates: Resume[] }>("/resume/search/", { params: { query }, signal })).data.matched_candidates; }
export async function rankCandidates(jobDescription: string) { return (await api.post<RankingResponse>("/resume/rank-candidates", null, { params: { job_description: jobDescription } })).data; }
export async function evaluateInvitations(input: { job_title: string; job_description: string; resume_ids: number[]; minimum_ats_score: number; mandatory_skills: string[]; require_all_mandatory_skills: boolean }) { return (await api.post<ScreeningSession>("/invitations/evaluate", input)).data; }
export async function sendInvitationBatch(id: number) { return (await api.post<ScreeningSession>(`/invitations/sessions/${id}/send`, { confirm: true })).data; }
export async function setInvitationAutomation(id: number, enabled: boolean) { return (await api.patch<ScreeningSession>(`/invitations/sessions/${id}/automation`, { enabled })).data; }
export async function processAutomaticInvitations(id: number) { return (await api.post<ScreeningSession>(`/invitations/sessions/${id}/automatic-send`)).data; }

export default api;
