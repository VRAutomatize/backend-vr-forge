-- ============================================================================
-- VRForge Backend - Schema Inicial Completo
-- ============================================================================
-- Este script cria todas as tabelas, índices, constraints e triggers
-- necessários para o funcionamento do VRForge Backend.
--
-- Versão: 1.0
-- Data: 2024
-- ============================================================================

-- Extension para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABELA: domains
-- Descrição: Domínios de negócio (VR Chat, VR Code, VR Lex, etc.)
-- ============================================================================
CREATE TABLE domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_domains_slug ON domains(slug);
CREATE INDEX idx_domains_is_active ON domains(is_active);
CREATE INDEX idx_domains_name ON domains(name);

COMMENT ON TABLE domains IS 'Domínios de negócio da VR Automatize (VR Chat, VR Code, VR Lex, etc.)';
COMMENT ON COLUMN domains.slug IS 'Slug único para identificação do domínio';
COMMENT ON COLUMN domains.config IS 'Configurações específicas do domínio em formato JSON';

-- ============================================================================
-- TABELA: documents
-- Descrição: Documentos uploadados pelos usuários
-- ============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    use_case VARCHAR(100),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    content_type VARCHAR(100),
    file_size BIGINT,
    status VARCHAR(50) DEFAULT 'uploaded',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_domain_id ON documents(domain_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_use_case ON documents(use_case);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

COMMENT ON TABLE documents IS 'Documentos uploadados para processamento';
COMMENT ON COLUMN documents.s3_key IS 'Chave do arquivo no AWS S3';
COMMENT ON COLUMN documents.status IS 'Status: uploaded, processing, processed, failed';

-- ============================================================================
-- TABELA: document_versions
-- Descrição: Versões processadas dos documentos
-- ============================================================================
CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    s3_key VARCHAR(500),
    extracted_text TEXT,
    processing_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, version_number)
);

CREATE INDEX idx_document_versions_document_id ON document_versions(document_id);
CREATE INDEX idx_document_versions_version_number ON document_versions(document_id, version_number);

COMMENT ON TABLE document_versions IS 'Versões processadas dos documentos com texto extraído';
COMMENT ON COLUMN document_versions.extracted_text IS 'Texto extraído do documento após processamento';

-- ============================================================================
-- TABELA: segments
-- Descrição: Segmentos de texto extraídos dos documentos
-- ============================================================================
CREATE TABLE segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    document_version_id UUID REFERENCES document_versions(id) ON DELETE SET NULL,
    use_case VARCHAR(100),
    segment_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_segments_domain_id ON segments(domain_id);
CREATE INDEX idx_segments_document_id ON segments(document_id);
CREATE INDEX idx_segments_document_version_id ON segments(document_version_id);
CREATE INDEX idx_segments_use_case ON segments(use_case);
CREATE INDEX idx_segments_segment_type ON segments(segment_type);
CREATE INDEX idx_segments_created_at ON segments(created_at DESC);

COMMENT ON TABLE segments IS 'Segmentos de texto extraídos dos documentos';
COMMENT ON COLUMN segments.segment_type IS 'Tipo: clause, chat_message, faq, crm_record, paragraph, etc.';
COMMENT ON COLUMN segments.position IS 'Posição do segmento no documento original';

-- ============================================================================
-- TABELA: generation_templates
-- Descrição: Templates para geração de datasets sintéticos
-- ============================================================================
CREATE TABLE generation_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    use_case VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    target_model_family VARCHAR(100),
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(domain_id, name)
);

CREATE INDEX idx_generation_templates_domain_id ON generation_templates(domain_id);
CREATE INDEX idx_generation_templates_use_case ON generation_templates(use_case);
CREATE INDEX idx_generation_templates_is_active ON generation_templates(is_active);
CREATE INDEX idx_generation_templates_target_model_family ON generation_templates(target_model_family);

COMMENT ON TABLE generation_templates IS 'Templates para geração de datasets sintéticos usando LLMs';
COMMENT ON COLUMN generation_templates.system_prompt IS 'Prompt do sistema para o LLM';
COMMENT ON COLUMN generation_templates.user_prompt_template IS 'Template do prompt do usuário (aceita {content} como placeholder)';

-- ============================================================================
-- TABELA: datasets
-- Descrição: Datasets de treinamento
-- ============================================================================
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    template_id UUID REFERENCES generation_templates(id) ON DELETE SET NULL,
    use_case VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    provider VARCHAR(50) NOT NULL,
    target_model_family VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    generation_config JSONB DEFAULT '{}',
    segment_filter JSONB DEFAULT '{}',
    total_items INTEGER DEFAULT 0,
    approved_items INTEGER DEFAULT 0,
    rejected_items INTEGER DEFAULT 0,
    pending_items INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_datasets_domain_id ON datasets(domain_id);
CREATE INDEX idx_datasets_template_id ON datasets(template_id);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_use_case ON datasets(use_case);
CREATE INDEX idx_datasets_provider ON datasets(provider);
CREATE INDEX idx_datasets_created_at ON datasets(created_at DESC);

COMMENT ON TABLE datasets IS 'Datasets de treinamento para modelos de IA';
COMMENT ON COLUMN datasets.provider IS 'Provider LLM usado: openai, gemini, together';
COMMENT ON COLUMN datasets.status IS 'Status: draft, generating, ready, archived';
COMMENT ON COLUMN datasets.segment_filter IS 'Filtros aplicados na seleção de segmentos em formato JSON';

-- ============================================================================
-- TABELA: dataset_items
-- Descrição: Items individuais do dataset (exemplos de treinamento)
-- ============================================================================
CREATE TABLE dataset_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    segment_id UUID REFERENCES segments(id) ON DELETE SET NULL,
    source_provider VARCHAR(50),
    instruction TEXT NOT NULL,
    input_text TEXT,
    ideal_response TEXT NOT NULL,
    bad_response TEXT,
    explanation TEXT,
    status VARCHAR(50) DEFAULT 'pending_review',
    quality_score FLOAT,
    quality_flags JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_dataset_items_dataset_id ON dataset_items(dataset_id);
CREATE INDEX idx_dataset_items_segment_id ON dataset_items(segment_id);
CREATE INDEX idx_dataset_items_status ON dataset_items(status);
CREATE INDEX idx_dataset_items_source_provider ON dataset_items(source_provider);
CREATE INDEX idx_dataset_items_quality_score ON dataset_items(quality_score DESC);
CREATE INDEX idx_dataset_items_created_at ON dataset_items(created_at DESC);

COMMENT ON TABLE dataset_items IS 'Items individuais do dataset (exemplos de treinamento)';
COMMENT ON COLUMN dataset_items.status IS 'Status: pending_review, approved, rejected';
COMMENT ON COLUMN dataset_items.quality_score IS 'Score de qualidade (0.0 a 1.0)';
COMMENT ON COLUMN dataset_items.quality_flags IS 'Flags de qualidade em formato JSON';

-- ============================================================================
-- TABELA: dataset_exports
-- Descrição: Histórico de exports de datasets
-- ============================================================================
CREATE TABLE dataset_exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    export_version INTEGER NOT NULL,
    format VARCHAR(20) DEFAULT 'jsonl',
    s3_key VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    item_count INTEGER DEFAULT 0,
    filters_applied JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(dataset_id, export_version)
);

CREATE INDEX idx_dataset_exports_dataset_id ON dataset_exports(dataset_id);
CREATE INDEX idx_dataset_exports_export_version ON dataset_exports(dataset_id, export_version DESC);
CREATE INDEX idx_dataset_exports_status ON dataset_exports(status);
CREATE INDEX idx_dataset_exports_created_at ON dataset_exports(created_at DESC);

COMMENT ON TABLE dataset_exports IS 'Histórico de exports de datasets para fine-tuning';
COMMENT ON COLUMN dataset_exports.format IS 'Formato do export: jsonl, json, csv';
COMMENT ON COLUMN dataset_exports.s3_key IS 'Chave do arquivo exportado no S3';

-- ============================================================================
-- TABELA: dataset_reviews
-- Descrição: Revisões humanas dos items do dataset
-- ============================================================================
CREATE TABLE dataset_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_item_id UUID NOT NULL REFERENCES dataset_items(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL,
    reviewer_id VARCHAR(100),
    justification TEXT,
    previous_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_dataset_reviews_dataset_item_id ON dataset_reviews(dataset_item_id);
CREATE INDEX idx_dataset_reviews_action ON dataset_reviews(action);
CREATE INDEX idx_dataset_reviews_reviewer_id ON dataset_reviews(reviewer_id);
CREATE INDEX idx_dataset_reviews_created_at ON dataset_reviews(created_at DESC);

COMMENT ON TABLE dataset_reviews IS 'Histórico de revisões humanas dos items do dataset';
COMMENT ON COLUMN dataset_reviews.action IS 'Ação: approve, reject, edit';
COMMENT ON COLUMN dataset_reviews.previous_values IS 'Valores anteriores antes da revisão';
COMMENT ON COLUMN dataset_reviews.new_values IS 'Novos valores após a revisão';

-- ============================================================================
-- TABELA: models
-- Descrição: Modelos de IA (base e fine-tunados)
-- ============================================================================
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_id UUID REFERENCES domains(id) ON DELETE SET NULL,
    name VARCHAR(200) NOT NULL UNIQUE,
    base_model VARCHAR(200) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_family VARCHAR(100),
    version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'registered',
    config JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_models_domain_id ON models(domain_id);
CREATE INDEX idx_models_provider ON models(provider);
CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_model_family ON models(model_family);
CREATE INDEX idx_models_name ON models(name);

COMMENT ON TABLE models IS 'Modelos de IA registrados (base e fine-tunados)';
COMMENT ON COLUMN models.base_model IS 'Modelo base (ex: llama-3.1-8b-instruct)';
COMMENT ON COLUMN models.provider IS 'Provider: openai, together, huggingface, etc.';
COMMENT ON COLUMN models.status IS 'Status: registered, training, deployed, archived';

-- ============================================================================
-- TABELA: training_jobs
-- Descrição: Jobs de treinamento de modelos
-- ============================================================================
CREATE TABLE training_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    dataset_export_id UUID REFERENCES dataset_exports(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending',
    provider VARCHAR(50) NOT NULL,
    external_job_id VARCHAR(200),
    hyperparameters JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_training_jobs_model_id ON training_jobs(model_id);
CREATE INDEX idx_training_jobs_dataset_id ON training_jobs(dataset_id);
CREATE INDEX idx_training_jobs_dataset_export_id ON training_jobs(dataset_export_id);
CREATE INDEX idx_training_jobs_status ON training_jobs(status);
CREATE INDEX idx_training_jobs_provider ON training_jobs(provider);
CREATE INDEX idx_training_jobs_external_job_id ON training_jobs(external_job_id);
CREATE INDEX idx_training_jobs_created_at ON training_jobs(created_at DESC);

COMMENT ON TABLE training_jobs IS 'Jobs de treinamento de modelos de IA';
COMMENT ON COLUMN training_jobs.status IS 'Status: pending, running, completed, failed, cancelled';
COMMENT ON COLUMN training_jobs.external_job_id IS 'ID do job no provider externo (Together, HuggingFace, etc.)';
COMMENT ON COLUMN training_jobs.metrics IS 'Métricas de treinamento em formato JSON';

-- ============================================================================
-- TABELA: system_logs
-- Descrição: Logs do sistema
-- ============================================================================
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL,
    module VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_id UUID,
    entity_type VARCHAR(50),
    details JSONB DEFAULT '{}',
    request_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_module ON system_logs(module);
CREATE INDEX idx_system_logs_action ON system_logs(action);
CREATE INDEX idx_system_logs_entity_id ON system_logs(entity_id);
CREATE INDEX idx_system_logs_entity_type ON system_logs(entity_type);
CREATE INDEX idx_system_logs_request_id ON system_logs(request_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at DESC);

COMMENT ON TABLE system_logs IS 'Logs estruturados do sistema';
COMMENT ON COLUMN system_logs.level IS 'Nível: DEBUG, INFO, WARNING, ERROR, CRITICAL';
COMMENT ON COLUMN system_logs.details IS 'Detalhes adicionais em formato JSON';

-- ============================================================================
-- FUNÇÃO: update_updated_at_column
-- Descrição: Função para atualizar automaticamente o campo updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

COMMENT ON FUNCTION update_updated_at_column() IS 'Função trigger para atualizar updated_at automaticamente';

-- ============================================================================
-- TRIGGERS: Atualização automática de updated_at
-- ============================================================================

CREATE TRIGGER update_domains_updated_at 
    BEFORE UPDATE ON domains
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_generation_templates_updated_at 
    BEFORE UPDATE ON generation_templates
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at 
    BEFORE UPDATE ON datasets
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dataset_items_updated_at 
    BEFORE UPDATE ON dataset_items
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_models_updated_at 
    BEFORE UPDATE ON models
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_jobs_updated_at 
    BEFORE UPDATE ON training_jobs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DADOS INICIAIS: Domínios padrão
-- ============================================================================

INSERT INTO domains (name, slug, description, config, is_active) VALUES
    ('VR Chat', 'vr-chat', 'IA conversacional geral baseada em Llama 3.1 8B', '{"primary_model": "llama-3.1-8b-instruct", "fallback_models": ["qwen2.5-32b-instruct", "deepseek-v3"]}', TRUE),
    ('VR Code', 'vr-code', 'Assistente de código baseado em Qwen2.5-Coder', '{"primary_model": "qwen2.5-coder-32b", "alternatives": ["qwen2.5-coder-7b", "deepseek-coder-v2"]}', TRUE),
    ('VR Data', 'vr-data', 'Análise de dados e SQL', '{}', TRUE),
    ('VR Lex', 'vr-lex', 'Jurídico com RAG e possível LoRA', '{"base_model": "qwen2.5-32b", "use_rag": true}', TRUE),
    ('VR Agent Brain', 'vr-agent-brain', 'Orquestrador inteligente com reasoning', '{"models": ["qwen3", "qwen2.5", "deepseek-r1"], "reasoning": true}', TRUE)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- VERIFICAÇÕES FINAIS
-- ============================================================================

-- Verificar se todas as tabelas foram criadas
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'domains', 'documents', 'document_versions', 'segments',
        'generation_templates', 'datasets', 'dataset_items',
        'dataset_exports', 'dataset_reviews', 'models',
        'training_jobs', 'system_logs'
    );
    
    IF table_count = 12 THEN
        RAISE NOTICE '✓ Todas as 12 tabelas foram criadas com sucesso!';
    ELSE
        RAISE WARNING 'Apenas % tabelas foram encontradas. Esperado: 12', table_count;
    END IF;
END $$;

-- ============================================================================
-- FIM DO SCRIPT
-- ============================================================================

