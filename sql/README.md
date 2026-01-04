# Scripts SQL do VRForge Backend

Este diretório contém os scripts SQL para criação e manutenção do banco de dados.

## Arquivos

### `001_initial_schema.sql`
Script completo para criação inicial do schema do banco de dados.

**Conteúdo:**
- Criação de todas as 12 tabelas
- Índices para performance
- Constraints e foreign keys
- Triggers para updated_at automático
- Dados iniciais (domínios padrão)
- Comentários em todas as tabelas e colunas

**Uso:**
```bash
psql -U vrforge -d vrforge -f sql/001_initial_schema.sql
```

### `002_rollback.sql`
Script para remover completamente o schema (apaga todos os dados!).

**Uso:**
```bash
psql -U vrforge -d vrforge -f sql/002_rollback.sql
```

## Estrutura das Tabelas

1. **domains** - Domínios de negócio
2. **documents** - Documentos uploadados
3. **document_versions** - Versões processadas
4. **segments** - Segmentos de texto
5. **generation_templates** - Templates de geração
6. **datasets** - Datasets de treinamento
7. **dataset_items** - Items do dataset
8. **dataset_exports** - Exports realizados
9. **dataset_reviews** - Revisões humanas
10. **models** - Modelos de IA
11. **training_jobs** - Jobs de treinamento
12. **system_logs** - Logs do sistema

## Execução

### Via psql
```bash
psql -U seu_usuario -d vrforge -f sql/001_initial_schema.sql
```

### Via Docker
```bash
docker exec -i vrforge_db psql -U vrforge -d vrforge < sql/001_initial_schema.sql
```

### Via Python (usando Alembic - recomendado)
```bash
alembic upgrade head
```

## Notas

- O script cria automaticamente os domínios padrão (VR Chat, VR Code, etc.)
- Todos os campos `updated_at` são atualizados automaticamente via triggers
- Os índices foram otimizados para queries frequentes
- O script é idempotente para alguns comandos (ON CONFLICT DO NOTHING)

## Migrações Futuras

Para novas migrações, use Alembic:

```bash
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```

