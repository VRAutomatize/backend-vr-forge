# 🚀 VRForge Backend

> Plataforma enterprise para forjar, gerenciar e treinar modelos de IA proprietários VR

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

**VRForge** é a plataforma oficial da **VR Automatize** para criação, gerenciamento e treinamento de modelos de IA proprietários, suportando múltiplos domínios de negócio e diferentes casos de uso.

## 🎯 Visão

O VRForge é a plataforma oficial da VR Automatize para **forjar modelos de IA proprietários VR**, suportando múltiplos domínios de negócio e diferentes casos de uso:

- **VR Chat** - IA conversacional geral
- **VR Code** - Assistente de código
- **VR Data** - Análise de dados e SQL
- **VR Lex** - Jurídico + RAG
- **VR Agent Brain** - Orquestrador inteligente
- Modelos rápidos (Phi-3 Mini, Qwen small)

## 🛠️ Stack Tecnológica

- **Python 3.11**
- **FastAPI** - Framework web assíncrono
- **PostgreSQL** - Banco de dados
- **SQLAlchemy** - ORM assíncrono
- **Alembic** - Migrações de banco
- **AWS S3** - Armazenamento de arquivos
- **Docker** - Containerização
- **Pydantic** - Validação de dados
- **Structlog** - Logging estruturado

## 📁 Estrutura do Projeto

```
/app
├── api/              # Endpoints da API REST
│   └── v1/          # Versão 1 da API
├── core/             # Configuração e utilitários core
├── db/               # Configuração do banco de dados
├── models/           # Modelos SQLAlchemy (11 modelos)
├── schemas/          # Schemas Pydantic para validação
├── services/         # Lógica de negócio (9 services)
├── integrations/     # Integrações externas
│   ├── s3_client.py
│   ├── llm_providers/  # OpenAI, Gemini, Together
│   └── text_extractors/ # PDF, DOCX, TXT
└── main.py           # Entry point FastAPI

/alembic/             # Migrações do banco de dados
/tests/               # Testes automatizados
```

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- Docker (opcional)

### Desenvolvimento Local

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/backend-vr-forge.git
cd backend-vr-forge

# 2. Crie e ative ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 5. Execute migrações
alembic upgrade head

# 6. Inicie o servidor
uvicorn app.main:app --reload
```

### Docker

```bash
# Build e start
docker-compose up --build

# Executar migrações
docker-compose exec api alembic upgrade head
```

A API estará disponível em:
- **Produção/Desenvolvimento**: `https://forge-server.grupo-vr.com:8000`
- **Local**: `http://localhost:8000` (se rodando localmente)

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: `https://forge-server.grupo-vr.com:8000/docs`
- **ReDoc**: `https://forge-server.grupo-vr.com:8000/redoc`
- **Health Check**: `https://forge-server.grupo-vr.com:8000/health`

## 🔌 Endpoints Principais

### Domains
- `POST /api/v1/domains` - Criar domínio
- `GET /api/v1/domains` - Listar domínios
- `GET /api/v1/domains/{id}` - Obter domínio
- `PUT /api/v1/domains/{id}` - Atualizar domínio

### Documents
- `POST /api/v1/documents/upload` - Upload documento
- `GET /api/v1/documents` - Listar documentos
- `GET /api/v1/documents/{id}` - Obter documento
- `POST /api/v1/documents/{id}/process` - Processar documento

### Segments
- `GET /api/v1/segments` - Listar segmentos (com filtros)
- `GET /api/v1/segments/{id}` - Obter segmento

### Templates
- `POST /api/v1/templates` - Criar template de geração
- `GET /api/v1/templates` - Listar templates
- `GET /api/v1/templates/{id}` - Obter template

### Datasets
- `POST /api/v1/datasets` - Criar dataset
- `GET /api/v1/datasets` - Listar datasets
- `GET /api/v1/datasets/{id}` - Obter dataset
- `POST /api/v1/datasets/generate` - Gerar items sintéticos

### Review
- `GET /api/v1/dataset/review/pending` - Listar items pendentes
- `POST /api/v1/dataset/review/{id}/approve` - Aprovar item
- `POST /api/v1/dataset/review/{id}/reject` - Rejeitar item
- `POST /api/v1/dataset/review/{id}/edit` - Editar item
- `GET /api/v1/dataset/review/{id}/history` - Histórico de revisões

### Export
- `POST /api/v1/datasets/{id}/export` - Exportar JSONL (formato Together)
- `GET /api/v1/datasets/{id}/exports` - Listar exports
- `GET /api/v1/exports/{id}/download` - URL de download

### Models & Training
- `GET /api/v1/models` - Listar modelos
- `POST /api/v1/models` - Registrar modelo
- `GET /api/v1/training-jobs` - Listar jobs de treinamento
- `POST /api/v1/training-jobs` - Criar job de treinamento

## 🗄️ Banco de Dados

### Modelos Implementados

1. **domains** - Domínios de negócio (VR Chat, VR Code, etc.)
2. **documents** - Documentos uploadados
3. **document_versions** - Versões processadas dos documentos
4. **segments** - Segmentos de texto extraídos
5. **generation_templates** - Templates para geração de datasets
6. **datasets** - Datasets de treinamento
7. **dataset_items** - Items individuais do dataset
8. **dataset_exports** - Histórico de exports
9. **dataset_reviews** - Revisões humanas
10. **models** - Modelos de IA registrados
11. **training_jobs** - Jobs de treinamento
12. **system_logs** - Logs do sistema

### Migrações

```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=app

# Testes específicos
pytest tests/test_domains.py
```

## 🔧 Configuração

### Variáveis de Ambiente

Veja `.env.example` para todas as variáveis necessárias:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/vrforge

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=vrforge-storage
AWS_S3_REGION=us-east-1

# LLM Providers
OPENAI_API_KEY=sk-...
GOOGLE_GEMINI_API_KEY=...
TOGETHER_API_KEY=...
```

## 🐳 Deploy

### EasyPanel

O projeto está preparado para deploy no EasyPanel:

1. Conecte o repositório GitHub
2. Configure as variáveis de ambiente
3. O build automático via Dockerfile será executado
4. Health check disponível em `/health`

### Dockerfile

O Dockerfile usa multi-stage build para otimizar o tamanho da imagem:

- Build stage: Compila dependências
- Runtime stage: Imagem final otimizada
- Healthcheck configurado
- Usuário não-root para segurança

## 📊 Fluxo de Trabalho

1. **Upload de Documentos** → Upload para S3
2. **Processamento** → Extração de texto e segmentação
3. **Geração de Dataset** → Criação sintética usando LLMs
4. **Revisão Humana** → Aprovação/rejeição de items
5. **Export** → Geração de JSONL para fine-tuning
6. **Treinamento** → Registro de jobs de treinamento

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário da VR Automatize.

## 📞 Suporte

Para questões e suporte, abra uma issue no GitHub.

---

**VRForge** - Forjando o futuro da IA VR 🚀
