# Alembic script.py template for autogenerate
"""add_raci_accountable_constraint

Revision ID: 656a3c5ba51a
Revises: cd9db7ed15ea
Create Date: 2026-05-19 16:40:53.096634
"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa



revision: str = '656a3c5ba51a'
down_revision: Union[str, None] = 'cd9db7ed15ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION check_raci_single_accountable()
        RETURNS TRIGGER AS $$
        DECLARE
            existing_count INT;
        BEGIN
            IF NEW.role = 'A' THEN
                SELECT COUNT(*) INTO existing_count
                FROM raci_assignments
                WHERE task_id = NEW.task_id AND role = 'A' AND id != NEW.id;
                IF existing_count > 0 THEN
                    RAISE EXCEPTION 'RACI_VALIDATION_FAILED: Task already has an Accountable (A)';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_raci_single_accountable ON raci_assignments;
        CREATE TRIGGER trg_raci_single_accountable
        BEFORE INSERT OR UPDATE ON raci_assignments
        FOR EACH ROW EXECUTE FUNCTION check_raci_single_accountable();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_raci_single_accountable ON raci_assignments;")
    op.execute("DROP FUNCTION IF EXISTS check_raci_single_accountable();")