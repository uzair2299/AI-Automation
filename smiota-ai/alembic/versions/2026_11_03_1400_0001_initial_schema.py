"""Initial database schema with pgvector and Smiota AI entities.

Revision ID: 0001
Revises:
Create Date: 2026-11-03 14:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Chat Sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('channel', sa.String(length=32), nullable=False),
        sa.Column('current_agent', sa.String(length=64), server_default='aiops', nullable=False),
        sa.Column('session_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_chat_sessions_id', 'chat_sessions', ['id'], unique=False)
    op.create_index('ix_chat_sessions_tenant_id', 'chat_sessions', ['tenant_id'], unique=False)
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'], unique=False)
    op.create_index('ix_chat_sessions_tenant_user', 'chat_sessions', ['tenant_id', 'user_id'], unique=False)

    # 3. Chat Messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('agent_name', sa.String(length=64), nullable=True),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_chat_messages_id', 'chat_messages', ['id'], unique=False)
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'], unique=False)

    # 4. Remediation Approvals table
    op.create_table(
        'remediation_approvals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('requested_by_user_id', sa.String(length=64), nullable=False),
        sa.Column('agent_name', sa.String(length=64), nullable=False),
        sa.Column('tool_name', sa.String(length=128), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('decision_reason', sa.Text(), nullable=True),
        sa.Column('decided_by_user_id', sa.String(length=64), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_result', sa.JSON(), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_remediation_approvals_id', 'remediation_approvals', ['id'], unique=False)
    op.create_index('ix_remediation_approvals_tenant_id', 'remediation_approvals', ['tenant_id'], unique=False)
    op.create_index('ix_remediation_approvals_session_id', 'remediation_approvals', ['session_id'], unique=False)
    op.create_index('ix_remediation_approvals_tool_name', 'remediation_approvals', ['tool_name'], unique=False)
    op.create_index('ix_remediation_approvals_status', 'remediation_approvals', ['status'], unique=False)
    op.create_index('ix_approvals_tenant_status', 'remediation_approvals', ['tenant_id', 'status'], unique=False)

    # 5. Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), nullable=False),
        sa.Column('channel', sa.String(length=32), nullable=False),
        sa.Column('agent_name', sa.String(length=64), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('tool_name', sa.String(length=128), nullable=True),
        sa.Column('tool_params', sa.JSON(), nullable=True),
        sa.Column('tool_output_summary', sa.Text(), nullable=True),
        sa.Column('remediation_approved_by', sa.String(length=128), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'], unique=False)
    op.create_index('ix_audit_logs_session_id', 'audit_logs', ['session_id'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_agent_name', 'audit_logs', ['agent_name'], unique=False)
    op.create_index('ix_audit_tenant_session', 'audit_logs', ['tenant_id', 'session_id'], unique=False)

    # 6. RAG Documents table with pgvector
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS rag_documents (
            document_id VARCHAR(64) PRIMARY KEY,
            title TEXT NOT NULL,
            category VARCHAR(64) NOT NULL DEFAULT 'general',
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            tags TEXT[] DEFAULT ARRAY[]::TEXT[],
            embedding vector(768)
        );
        """
    )
    op.create_index('ix_rag_documents_category', 'rag_documents', ['category'], unique=False)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS rag_documents;")
    op.drop_table('audit_logs')
    op.drop_table('remediation_approvals')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')

