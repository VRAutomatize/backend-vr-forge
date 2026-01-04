"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extension para UUID
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # DOMAINS
    op.create_table(
        'domains',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_domains_slug', 'domains', ['slug'])
    op.create_index('idx_domains_is_active', 'domains', ['is_active'])

    # DOCUMENTS
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('domain_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('s3_key', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE')
    )
    op.create_index('idx_documents_domain_id', 'documents', ['domain_id'])
    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_documents_use_case', 'documents', ['use_case'])

    # DOCUMENT_VERSIONS
    op.create_table(
        'document_versions',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('s3_key', sa.String(length=500), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('processing_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('document_id', 'version_number')
    )
    op.create_index('idx_document_versions_document_id', 'document_versions', ['document_id'])

    # SEGMENTS
    op.create_table(
        'segments',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('domain_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('document_version_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('segment_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['document_version_id'], ['document_versions.id'], ondelete='SET NULL')
    )
    op.create_index('idx_segments_domain_id', 'segments', ['domain_id'])
    op.create_index('idx_segments_document_id', 'segments', ['document_id'])
    op.create_index('idx_segments_use_case', 'segments', ['use_case'])
    op.create_index('idx_segments_segment_type', 'segments', ['segment_type'])

    # GENERATION_TEMPLATES
    op.create_table(
        'generation_templates',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('domain_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('user_prompt_template', sa.Text(), nullable=False),
        sa.Column('target_model_family', sa.String(length=100), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('domain_id', 'name')
    )
    op.create_index('idx_generation_templates_domain_id', 'generation_templates', ['domain_id'])
    op.create_index('idx_generation_templates_use_case', 'generation_templates', ['use_case'])

    # DATASETS
    op.create_table(
        'datasets',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('domain_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('target_model_family', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('generation_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('segment_filter', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('approved_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rejected_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pending_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['generation_templates.id'], ondelete='SET NULL')
    )
    op.create_index('idx_datasets_domain_id', 'datasets', ['domain_id'])
    op.create_index('idx_datasets_status', 'datasets', ['status'])
    op.create_index('idx_datasets_use_case', 'datasets', ['use_case'])

    # DATASET_ITEMS
    op.create_table(
        'dataset_items',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('segment_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('source_provider', sa.String(length=50), nullable=True),
        sa.Column('instruction', sa.Text(), nullable=False),
        sa.Column('input_text', sa.Text(), nullable=True),
        sa.Column('ideal_response', sa.Text(), nullable=False),
        sa.Column('bad_response', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending_review'),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('quality_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['segment_id'], ['segments.id'], ondelete='SET NULL')
    )
    op.create_index('idx_dataset_items_dataset_id', 'dataset_items', ['dataset_id'])
    op.create_index('idx_dataset_items_status', 'dataset_items', ['status'])
    op.create_index('idx_dataset_items_segment_id', 'dataset_items', ['segment_id'])

    # DATASET_EXPORTS
    op.create_table(
        'dataset_exports',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('export_version', sa.Integer(), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=False, server_default='jsonl'),
        sa.Column('s3_key', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('item_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('filters_applied', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('dataset_id', 'export_version')
    )
    op.create_index('idx_dataset_exports_dataset_id', 'dataset_exports', ['dataset_id'])

    # DATASET_REVIEWS
    op.create_table(
        'dataset_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('dataset_item_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('reviewer_id', sa.String(length=100), nullable=True),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('previous_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dataset_item_id'], ['dataset_items.id'], ondelete='CASCADE')
    )
    op.create_index('idx_dataset_reviews_dataset_item_id', 'dataset_reviews', ['dataset_item_id'])
    op.create_index('idx_dataset_reviews_action', 'dataset_reviews', ['action'])

    # MODELS
    op.create_table(
        'models',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('domain_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('base_model', sa.String(length=200), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_family', sa.String(length=100), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='registered'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='SET NULL')
    )
    op.create_index('idx_models_domain_id', 'models', ['domain_id'])
    op.create_index('idx_models_provider', 'models', ['provider'])
    op.create_index('idx_models_status', 'models', ['status'])

    # TRAINING_JOBS
    op.create_table(
        'training_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('model_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('dataset_export_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('external_job_id', sa.String(length=200), nullable=True),
        sa.Column('hyperparameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_export_id'], ['dataset_exports.id'], ondelete='SET NULL')
    )
    op.create_index('idx_training_jobs_model_id', 'training_jobs', ['model_id'])
    op.create_index('idx_training_jobs_dataset_id', 'training_jobs', ['dataset_id'])
    op.create_index('idx_training_jobs_status', 'training_jobs', ['status'])

    # SYSTEM_LOGS
    op.create_table(
        'system_logs',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('module', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_logs_level', 'system_logs', ['level'])
    op.create_index('idx_system_logs_module', 'system_logs', ['module'])
    op.create_index('idx_system_logs_entity_id', 'system_logs', ['entity_id'])
    op.create_index('idx_system_logs_created_at', 'system_logs', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # Função para atualizar updated_at automaticamente
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Triggers para updated_at
    op.execute("""
        CREATE TRIGGER update_domains_updated_at BEFORE UPDATE ON domains
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_generation_templates_updated_at BEFORE UPDATE ON generation_templates
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_dataset_items_updated_at BEFORE UPDATE ON dataset_items
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_training_jobs_updated_at BEFORE UPDATE ON training_jobs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS update_training_jobs_updated_at ON training_jobs;')
    op.execute('DROP TRIGGER IF EXISTS update_models_updated_at ON models;')
    op.execute('DROP TRIGGER IF EXISTS update_dataset_items_updated_at ON dataset_items;')
    op.execute('DROP TRIGGER IF EXISTS update_datasets_updated_at ON datasets;')
    op.execute('DROP TRIGGER IF EXISTS update_generation_templates_updated_at ON generation_templates;')
    op.execute('DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;')
    op.execute('DROP TRIGGER IF EXISTS update_domains_updated_at ON domains;')
    
    # Drop function
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column();')
    
    # Drop tables in reverse order
    op.drop_table('system_logs')
    op.drop_table('training_jobs')
    op.drop_table('models')
    op.drop_table('dataset_reviews')
    op.drop_table('dataset_exports')
    op.drop_table('dataset_items')
    op.drop_table('datasets')
    op.drop_table('generation_templates')
    op.drop_table('segments')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('domains')

