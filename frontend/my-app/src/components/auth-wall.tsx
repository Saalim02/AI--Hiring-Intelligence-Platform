import Link from "next/link";

export default function AuthWall() {
  return (
    <main className="auth-wall">
      <div className="auth-card">
        <div className="brand">
          <span className="brand-mark">H</span>
          <span>hirewise</span>
        </div>
        <p className="eyebrow">Private screening workspace</p>
        <h1>Your hiring signal, clearer.</h1>
        <p className="muted">Sign in to access your resume intelligence workspace.</p>
        <Link className="button primary full" href="/login">Continue to sign in</Link>
        <Link className="button secondary full" href="/signup">Create an account</Link>
      </div>
    </main>
  );
}
