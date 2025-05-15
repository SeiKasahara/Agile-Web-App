"""Auto migration

Revision ID: 62b8f2ca88f0
Revises: 6c47205a80fc
Create Date: 2025-05-06 15:19:50.021703

"""
from alembic import op, context
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62b8f2ca88f0'
down_revision = '6c47205a80fc'
branch_labels = None
depends_on = None

def upgrade():
    conn  = op.get_bind()
    result = conn.execute(sa.text("PRAGMA table_info('users')"))
    existing_cols = {row[1] for row in result.fetchall()}
    if 'default_fuel_type' not in existing_cols:
       op.add_column('users',
              sa.Column('default_fuel_type', sa.String(32), nullable=True)
       )
    if 'default_date_range' not in existing_cols:
       op.add_column('users',
              sa.Column('default_date_range', sa.String(16), nullable=True)
       )
    if 'default_location' not in existing_cols:
       op.add_column('users',
              sa.Column('default_location', sa.String(64), nullable=True)
       )
    if 'alert_threshold' not in existing_cols:
       op.add_column('users',
              sa.Column('alert_threshold', sa.Float(), nullable=True)
       )
    if 'alert_frequency' not in existing_cols:
       op.add_column('users',
              sa.Column('alert_frequency', sa.String(16), nullable=True)
       )
    if 'public_dashboard' not in existing_cols:
       op.add_column('users',
              sa.Column('public_dashboard', sa.Boolean(), nullable=True)
       )

    if context.get_context().dialect.name == 'sqlite':
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column('avatar',
                existing_type=sa.TEXT(),
                type_=sa.String(length=256),
                existing_nullable=True
            )
            batch_op.alter_column('email_verify_code',
                existing_type=sa.TEXT(),
                type_=sa.String(length=6),
                existing_nullable=True
            )
            batch_op.alter_column('email_verify_expiration',
                existing_type=sa.TEXT(),
                type_=sa.DateTime(),
                existing_nullable=True
            )

def downgrade():
    if context.get_context().dialect.name == 'sqlite':
        with op.batch_alter_table('users') as batch_op:
            batch_op.alter_column('email_verify_expiration',
                existing_type=sa.DateTime(),
                type_=sa.TEXT(),
                existing_nullable=True
            )
            batch_op.alter_column('email_verify_code',
                existing_type=sa.String(length=6),
                type_=sa.TEXT(),
                existing_nullable=True
            )
            batch_op.alter_column('avatar',
                existing_type=sa.String(length=256),
                type_=sa.TEXT(),
                existing_nullable=True
            )

    for col in [
        'public_dashboard', 'alert_frequency', 'alert_threshold',
        'default_location', 'default_date_range', 'default_fuel_type'
    ]:
        op.drop_column('users', col)
