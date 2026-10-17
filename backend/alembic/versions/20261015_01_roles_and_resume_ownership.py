"""Add account roles and safe resume ownership."""
from alembic import op
import sqlalchemy as sa

revision = "20261015_01"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("username", sa.String(), nullable=True),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("hashed_password", sa.String(), nullable=True),
            sa.UniqueConstraint("username"),
            sa.UniqueConstraint("email"),
        )
    if "resumes" not in tables:
        op.create_table(
            "resumes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("filename", sa.String(), nullable=True),
            sa.Column("extracted_text", sa.Text(), nullable=True),
            sa.Column("skills", sa.Text(), nullable=True),
        )
    inspector = sa.inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "role" not in user_columns:
        # The server default backfills existing rows atomically and gives new rows
        # a safe role. Keep it in place for databases created from this revision.
        op.add_column("users", sa.Column("role", sa.String(length=20), nullable=False, server_default="recruiter"))
    constraints = {constraint.get("name") for constraint in inspector.get_check_constraints("users")}
    if "ck_users_role" not in constraints:
        op.create_check_constraint("ck_users_role", "users", "role IN ('recruiter', 'candidate')")

    resume_columns = {column["name"] for column in inspector.get_columns("resumes")}
    if "owner_id" not in resume_columns:
        op.add_column("resumes", sa.Column("owner_id", sa.Integer(), nullable=True))
    indexes = {index["name"] for index in inspector.get_indexes("resumes")}
    if "ix_resumes_owner_id" not in indexes:
        op.create_index("ix_resumes_owner_id", "resumes", ["owner_id"])
    foreign_keys = {foreign_key.get("name") for foreign_key in inspector.get_foreign_keys("resumes")}
    if "fk_resumes_owner_id_users" not in foreign_keys:
        op.create_foreign_key("fk_resumes_owner_id_users", "resumes", "users", ["owner_id"], ["id"], ondelete="SET NULL")

def downgrade():
    op.drop_constraint("fk_resumes_owner_id_users", "resumes", type_="foreignkey")
    op.drop_index("ix_resumes_owner_id", table_name="resumes")
    op.drop_column("resumes", "owner_id")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
