"""Add recruiter screening sessions and invitation tracking."""
from alembic import op
import sqlalchemy as sa

revision = "20261015_02"
down_revision = "20261015_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("resumes", sa.Column("candidate_name", sa.String(length=200), nullable=True))
    op.add_column("resumes", sa.Column("extracted_email", sa.String(length=320), nullable=True))
    op.create_index("ix_resumes_extracted_email", "resumes", ["extracted_email"])
    op.create_table(
        "screening_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recruiter_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_title", sa.String(length=200), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("minimum_ats_score", sa.Float(), nullable=False, server_default="85"),
        sa.Column("mandatory_skills", sa.JSON(), nullable=False),
        sa.Column("require_all_mandatory_skills", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("automatic_invitations_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("first_batch_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_screening_sessions_recruiter_id", "screening_sessions", ["recruiter_id"])
    op.create_table(
        "invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_email", sa.String(length=320), nullable=True),
        sa.Column("candidate_name", sa.String(length=200), nullable=True),
        sa.Column("score_snapshot", sa.Float(), nullable=True),
        sa.Column("matched_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("eligible", sa.Boolean(), nullable=False),
        sa.Column("eligibility_reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("session_id", "resume_id", name="uq_invitations_session_resume"),
    )
    op.create_index("ix_invitations_session_id", "invitations", ["session_id"])
    op.create_index("ix_invitations_resume_id", "invitations", ["resume_id"])
    op.create_index("ix_invitations_status", "invitations", ["status"])


def downgrade():
    op.drop_table("invitations")
    op.drop_table("screening_sessions")
    op.drop_index("ix_resumes_extracted_email", table_name="resumes")
    op.drop_column("resumes", "extracted_email")
    op.drop_column("resumes", "candidate_name")
