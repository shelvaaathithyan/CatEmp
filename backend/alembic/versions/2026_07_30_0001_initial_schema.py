"""Initial database schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-07-30 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. customers
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)

    # 3. dealers
    op.create_table(
        'dealers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dealers_id'), 'dealers', ['id'], unique=False)

    # 4. sites
    op.create_table(
        'sites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('site_code', sa.String(length=20), nullable=False),
        sa.Column('site_name', sa.String(length=100), nullable=False),
        sa.Column('location', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sites_id'), 'sites', ['id'], unique=False)

    # 5. fleet_managers
    op.create_table(
        'fleet_managers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fleet_managers_id'), 'fleet_managers', ['id'], unique=False)

    # 6. operators
    op.create_table(
        'operators',
        sa.Column('operator_id', sa.String(length=20), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('operator_name', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('operator_id')
    )
    op.create_index(op.f('ix_operators_operator_id'), 'operators', ['operator_id'], unique=False)

    # 7. machines
    op.create_table(
        'machines',
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('dealer_id', sa.Integer(), nullable=False),
        sa.Column('equipment_type', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(['dealer_id'], ['dealers.id'], ),
        sa.PrimaryKeyConstraint('equipment_id')
    )
    op.create_index(op.f('ix_machines_equipment_id'), 'machines', ['equipment_id'], unique=False)

    # 8. rentals
    op.create_table(
        'rentals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('fleet_manager_id', sa.Integer(), nullable=False),
        sa.Column('check_in_date', sa.Date(), nullable=True),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('actual_return_date', sa.Date(), nullable=True),
        sa.Column('rental_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('rental_status', sa.String(length=30), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.ForeignKeyConstraint(['fleet_manager_id'], ['fleet_managers.id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rentals_id'), 'rentals', ['id'], unique=False)

    # 9. site_transfers
    op.create_table(
        'site_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rental_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('from_site_id', sa.Integer(), nullable=False),
        sa.Column('to_site_id', sa.Integer(), nullable=False),
        sa.Column('transfer_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('transferred_by', sa.Integer(), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.ForeignKeyConstraint(['from_site_id'], ['sites.id'], ),
        sa.ForeignKeyConstraint(['rental_id'], ['rentals.id'], ),
        sa.ForeignKeyConstraint(['to_site_id'], ['sites.id'], ),
        sa.ForeignKeyConstraint(['transferred_by'], ['fleet_managers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_site_transfers_id'), 'site_transfers', ['id'], unique=False)

    # 10. checkin_checkout
    op.create_table(
        'checkin_checkout',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rental_id', sa.Integer(), nullable=False),
        sa.Column('performed_by', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['performed_by'], ['fleet_managers.id'], ),
        sa.ForeignKeyConstraint(['rental_id'], ['rentals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkin_checkout_id'), 'checkin_checkout', ['id'], unique=False)

    # 11. equipment_usage
    op.create_table(
        'equipment_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rental_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('engine_hours_per_day', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('idle_hours_per_day', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('rental_days', sa.Integer(), nullable=True),
        sa.Column('last_operator_id', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.ForeignKeyConstraint(['last_operator_id'], ['operators.operator_id'], ),
        sa.ForeignKeyConstraint(['rental_id'], ['rentals.id'], ),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipment_usage_id'), 'equipment_usage', ['id'], unique=False)

    # 12. maintenance_history
    op.create_table(
        'maintenance_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('service_date', sa.Date(), nullable=False),
        sa.Column('service_type', sa.String(length=100), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_history_id'), 'maintenance_history', ['id'], unique=False)

    # 13. maintenance_predictions
    op.create_table(
        'maintenance_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('prediction_timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('maintenance_probability', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('predicted_service_date', sa.Date(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_predictions_id'), 'maintenance_predictions', ['id'], unique=False)

    # 14. utilization_predictions
    op.create_table(
        'utilization_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prediction_timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('utilization_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('predicted_idle_hours', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_utilization_predictions_id'), 'utilization_predictions', ['id'], unique=False)

    # 15. demand_predictions
    op.create_table(
        'demand_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prediction_timestamp', sa.TIMESTAMP(), nullable=False),
        sa.Column('equipment_type', sa.String(length=50), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('prediction_period', sa.String(length=30), nullable=True),
        sa.Column('expected_demand', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demand_predictions_id'), 'demand_predictions', ['id'], unique=False)

    # 16. notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=True),
        sa.Column('notification_type', sa.String(length=30), nullable=True),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['machines.equipment_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_demand_predictions_id'), table_name='demand_predictions')
    op.drop_table('demand_predictions')
    op.drop_index(op.f('ix_utilization_predictions_id'), table_name='utilization_predictions')
    op.drop_table('utilization_predictions')
    op.drop_index(op.f('ix_maintenance_predictions_id'), table_name='maintenance_predictions')
    op.drop_table('maintenance_predictions')
    op.drop_index(op.f('ix_maintenance_history_id'), table_name='maintenance_history')
    op.drop_table('maintenance_history')
    op.drop_index(op.f('ix_equipment_usage_id'), table_name='equipment_usage')
    op.drop_table('equipment_usage')
    op.drop_index(op.f('ix_checkin_checkout_id'), table_name='checkin_checkout')
    op.drop_table('checkin_checkout')
    op.drop_index(op.f('ix_site_transfers_id'), table_name='site_transfers')
    op.drop_table('site_transfers')
    op.drop_index(op.f('ix_rentals_id'), table_name='rentals')
    op.drop_table('rentals')
    op.drop_index(op.f('ix_machines_equipment_id'), table_name='machines')
    op.drop_table('machines')
    op.drop_index(op.f('ix_operators_operator_id'), table_name='operators')
    op.drop_table('operators')
    op.drop_index(op.f('ix_fleet_managers_id'), table_name='fleet_managers')
    op.drop_table('fleet_managers')
    op.drop_index(op.f('ix_sites_id'), table_name='sites')
    op.drop_table('sites')
    op.drop_index(op.f('ix_dealers_id'), table_name='dealers')
    op.drop_table('dealers')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
