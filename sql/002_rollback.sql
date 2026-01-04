-- ============================================================================
-- VRForge Backend - Script de Rollback
-- ============================================================================
-- Este script remove todas as tabelas, triggers e funções criadas
-- ATENÇÃO: Este script apaga TODOS os dados!
-- ============================================================================

-- Remover triggers
DROP TRIGGER IF EXISTS update_training_jobs_updated_at ON training_jobs;
DROP TRIGGER IF EXISTS update_models_updated_at ON models;
DROP TRIGGER IF EXISTS update_dataset_items_updated_at ON dataset_items;
DROP TRIGGER IF EXISTS update_datasets_updated_at ON datasets;
DROP TRIGGER IF EXISTS update_generation_templates_updated_at ON generation_templates;
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
DROP TRIGGER IF EXISTS update_domains_updated_at ON domains;

-- Remover função
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Remover tabelas (em ordem de dependência)
DROP TABLE IF EXISTS system_logs CASCADE;
DROP TABLE IF EXISTS training_jobs CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS dataset_reviews CASCADE;
DROP TABLE IF EXISTS dataset_exports CASCADE;
DROP TABLE IF EXISTS dataset_items CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;
DROP TABLE IF EXISTS generation_templates CASCADE;
DROP TABLE IF EXISTS segments CASCADE;
DROP TABLE IF EXISTS document_versions CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS domains CASCADE;

-- Remover extension (opcional - comentado para não afetar outros bancos)
-- DROP EXTENSION IF EXISTS "uuid-ossp";

RAISE NOTICE 'Rollback completo! Todas as tabelas foram removidas.';

