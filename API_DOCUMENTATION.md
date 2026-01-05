# VR Forge Backend - Documentação Completa da API

## Índice

1. [Informações Gerais](#informações-gerais)
2. [Autenticação e Headers](#autenticação-e-headers)
3. [Tratamento de Erros](#tratamento-de-erros)
4. [Health Check](#health-check)
5. [Domains](#domains)
6. [Documents](#documents)
7. [Segments](#segments)
8. [Templates](#templates)
9. [Datasets](#datasets)
10. [Review](#review)
11. [Export](#export)
12. [Models](#models)
13. [Training Jobs](#training-jobs)

---

## Informações Gerais

### Base URL

- **Desenvolvimento/Produção:** `https://forge-server.grupo-vr.com`
- **Local (opcional):** `http://localhost:8000`

**Nota:** O servidor está atrás de um proxy reverso, então não é necessário especificar a porta na URL pública. Configure via variável de ambiente `NEXT_PUBLIC_API_URL` no frontend.

### Versão da API

- **Versão Atual:** `v1`
- **Prefixo Base:** `/api/v1`
- **Exceção:** Health check está em `/health` (sem prefixo)
- **URL Completa Base:** `https://forge-server.grupo-vr.com/api/v1`

### Formato de Dados

- **Content-Type:** `application/json` (exceto upload de arquivos: `multipart/form-data`)
- **Accept:** `application/json`
- **Encoding:** UTF-8

### Resumo Rápido das Rotas

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Health check (sem prefixo `/api/v1`) |
| `GET` | `/api/v1/domains` | Listar domínios |
| `POST` | `/api/v1/domains` | Criar domínio |
| `GET` | `/api/v1/domains/{id}` | Obter domínio |
| `PUT` | `/api/v1/domains/{id}` | Atualizar domínio |
| `POST` | `/api/v1/documents/upload` | Upload documento (multipart/form-data) |
| `GET` | `/api/v1/documents` | Listar documentos |
| `GET` | `/api/v1/documents/{id}` | Obter documento |
| `POST` | `/api/v1/documents/{id}/process` | Processar documento |
| `GET` | `/api/v1/segments` | Listar segmentos |
| `GET` | `/api/v1/segments/{id}` | Obter segmento |
| `POST` | `/api/v1/templates` | Criar template |
| `GET` | `/api/v1/templates` | Listar templates |
| `GET` | `/api/v1/templates/{id}` | Obter template |
| `POST` | `/api/v1/datasets` | Criar dataset |
| `GET` | `/api/v1/datasets` | Listar datasets |
| `GET` | `/api/v1/datasets/{id}` | Obter dataset |
| `POST` | `/api/v1/datasets/generate` | Gerar items sintéticos |
| `GET` | `/api/v1/dataset/review/pending` | Listar items pendentes |
| `POST` | `/api/v1/dataset/review/{id}/approve` | Aprovar item |
| `POST` | `/api/v1/dataset/review/{id}/reject` | Rejeitar item |
| `POST` | `/api/v1/dataset/review/{id}/edit` | Editar item |
| `POST` | `/api/v1/datasets/{id}/export` | Exportar dataset |
| `GET` | `/api/v1/datasets/{id}/exports` | Listar exports |
| `GET` | `/api/v1/datasets/exports/{id}/download` | Download export |
| `POST` | `/api/v1/models` | Registrar modelo |
| `GET` | `/api/v1/models` | Listar modelos |
| `GET` | `/api/v1/models/{id}` | Obter modelo |
| `POST` | `/api/v1/training-jobs` | Criar job de treinamento |
| `GET` | `/api/v1/training-jobs` | Listar jobs |
| `GET` | `/api/v1/training-jobs/{id}` | Obter job |

### Request ID

Todas as requisições recebem um `X-Request-ID` único no header da resposta. Use este ID para rastreamento e debug.

### ⚠️ IMPORTANTE: Requisições HTTP Válidas

**O backend detecta e loga requisições HTTP inválidas ou malformadas.** Para evitar erros, siga estas diretrizes:

1. **Sempre use URLs completas:**
   - ✅ Correto: `https://forge-server.grupo-vr.com/api/v1/domains`
   - ❌ Errado: `/api/v1/domains` (sem protocolo/host)
   - ❌ Errado: `api/v1/domains` (sem barra inicial)
   - ❌ Errado: `https://forge-server.grupo-vr.com:8000/api/v1/domains` (não incluir porta na URL pública)

2. **Use os métodos HTTP corretos:**
   - `GET` para listar/obter recursos
   - `POST` para criar recursos
   - `PUT` para atualizar recursos

3. **Headers obrigatórios:**
   ```http
   Content-Type: application/json
   Accept: application/json
   ```
   Exceção: Uploads usam `multipart/form-data` (sem header Content-Type manual)

4. **Body JSON válido:**
   - Sempre envie JSON válido quando usar `Content-Type: application/json`
   - Não envie strings vazias ou dados malformados
   - Valide o JSON antes de enviar

5. **Query parameters na URL:**
   - ✅ Correto: `/api/v1/documents/upload?domain_id=xxx&use_case=yyy`
   - ❌ Errado: Enviar query params no body

**Se você ver "Invalid HTTP request received" nos logs:**
- Verifique se a URL está completa e correta
- Confirme que os headers estão corretos
- Valide que o body JSON está bem formado (se aplicável)
- Certifique-se de usar o método HTTP correto

---

## Autenticação e Headers

### Headers Padrão

```http
Content-Type: application/json
Accept: application/json
```

### Headers de Resposta

```http
X-Request-ID: abc123def456
Content-Type: application/json
```

**Nota:** Autenticação não está implementada ainda. Headers de autenticação serão adicionados em versões futuras.

---

## Tratamento de Erros

### Formato Padrão de Erro

```json
{
  "error": "Mensagem de erro descritiva",
  "details": {
    "campo_específico": "Detalhes adicionais"
  },
  "request_id": "abc123def456"
}
```

### Status Codes

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 202 | Aceito (processamento assíncrono iniciado) |
| 400 | Requisição inválida |
| 404 | Recurso não encontrado |
| 422 | Erro de validação |
| 500 | Erro interno do servidor |
| 502 | Erro em serviço externo |

### Exemplos de Erros

**404 Not Found:**
```json
{
  "error": "Document with id 'xyz' not found",
  "details": {},
  "request_id": "abc123"
}
```

**422 Validation Error:**
```json
{
  "error": "Validation failed",
  "details": {
    "name": "Field required",
    "slug": "Invalid format"
  },
  "request_id": "abc123"
}
```

---

## Health Check

### GET `/health`

Verifica se o serviço está online.

**Resposta:**
```json
{
  "status": "healthy"
}
```

**Status Code:** `200`

---

### GET `/health/detailed`

Health check detalhado com informações do serviço.

**Resposta:**
```json
{
  "status": "healthy",
  "service": "VRForge",
  "version": "0.1.0"
}
```

**Status Code:** `200`

---

## Domains

Gerenciamento de domínios de negócio (VR Chat, VR Code, VR Lex, etc.).

### POST `/api/v1/domains`

Cria um novo domínio.

**Request Body:**
```json
{
  "name": "VR Chat",
  "slug": "vr-chat",
  "description": "IA conversacional geral",
  "config": {
    "primary_model": "llama-3.1-8b-instruct"
  }
}
```

**Campos:**
- `name` (string, obrigatório, 1-100 caracteres): Nome do domínio
- `slug` (string, obrigatório, 1-100 caracteres): Slug único (ex: "vr-chat")
- `description` (string, opcional): Descrição do domínio
- `config` (object, opcional): Configurações específicas em JSON

**Response:** `201 Created`
```json
{
  "id": "uuid-do-dominio",
  "name": "VR Chat",
  "slug": "vr-chat",
  "description": "IA conversacional geral",
  "config": {
    "primary_model": "llama-3.1-8b-instruct"
  },
  "is_active": true,
  "created_at": "2024-01-04T22:27:51.828844Z",
  "updated_at": "2024-01-04T22:27:51.828844Z"
}
```

---

### GET `/api/v1/domains`

Lista todos os domínios.

**Query Parameters:**
- `active_only` (boolean, opcional, default: `true`): Retornar apenas domínios ativos

**Exemplo:**
```
GET /api/v1/domains?active_only=true
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-1",
    "name": "VR Chat",
    "slug": "vr-chat",
    "description": "IA conversacional",
    "config": {},
    "is_active": true,
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:27:51Z"
  },
  {
    "id": "uuid-2",
    "name": "VR Code",
    "slug": "vr-code",
    "description": "Assistente de código",
    "config": {},
    "is_active": true,
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:27:51Z"
  }
]
```

---

### GET `/api/v1/domains/{domain_id}`

Obtém um domínio específico por ID.

**Path Parameters:**
- `domain_id` (string, UUID): ID do domínio

**Response:** `200 OK`
```json
{
  "id": "uuid-do-dominio",
  "name": "VR Chat",
  "slug": "vr-chat",
  "description": "IA conversacional geral",
  "config": {},
  "is_active": true,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Domínio não encontrado

---

### PUT `/api/v1/domains/{domain_id}`

Atualiza um domínio existente.

**Path Parameters:**
- `domain_id` (string, UUID): ID do domínio

**Request Body:**
```json
{
  "name": "VR Chat Updated",
  "slug": "vr-chat-updated",
  "description": "Nova descrição",
  "config": {
    "new_field": "value"
  },
  "is_active": false
}
```

**Campos (todos opcionais):**
- `name` (string, 1-100 caracteres)
- `slug` (string, 1-100 caracteres)
- `description` (string)
- `config` (object)
- `is_active` (boolean)

**Response:** `200 OK`
```json
{
  "id": "uuid-do-dominio",
  "name": "VR Chat Updated",
  "slug": "vr-chat-updated",
  "description": "Nova descrição",
  "config": {
    "new_field": "value"
  },
  "is_active": false,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:28:00Z"
}
```

**Erros:**
- `404`: Domínio não encontrado

---

## Documents

Upload e processamento de documentos (PDF, DOCX, TXT).

### POST `/api/v1/documents/upload`

Upload de um documento.

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` (File, obrigatório): Arquivo a ser enviado (PDF, DOCX ou TXT)
- `domain_id` (string, query parameter, obrigatório): ID do domínio
- `use_case` (string, query parameter, opcional): Caso de uso

**Exemplo de Request:**
```http
POST /api/v1/documents/upload?domain_id=uuid-do-dominio&use_case=chat-training
Content-Type: multipart/form-data

file: [arquivo.pdf]
```

**Response:** `201 Created`
```json
{
  "id": "uuid-do-documento",
  "domain_id": "uuid-do-dominio",
  "use_case": "chat-training",
  "filename": "documento.pdf",
  "original_filename": "documento.pdf",
  "s3_key": "documents/uuid-do-dominio/uuid/documento.pdf",
  "content_type": "application/pdf",
  "file_size": 1024000,
  "status": "uploaded",
  "metadata": {},
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Status Possíveis:**
- `uploaded`: Documento enviado, aguardando processamento
- `processing`: Processamento em andamento
- `processed`: Processado com sucesso
- `failed`: Falha no processamento

**Erros:**
- `404`: Domínio não encontrado
- `422`: Arquivo inválido ou tipo não suportado

---

### GET `/api/v1/documents`

Lista todos os documentos.

**Query Parameters:**
- `domain_id` (string, opcional): Filtrar por domínio

**Exemplo:**
```
GET /api/v1/documents?domain_id=uuid-do-dominio
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-1",
    "domain_id": "uuid-do-dominio",
    "use_case": "chat-training",
    "filename": "doc1.pdf",
    "original_filename": "doc1.pdf",
    "s3_key": "documents/.../doc1.pdf",
    "content_type": "application/pdf",
    "file_size": 1024000,
    "status": "processed",
    "metadata": {},
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:27:51Z"
  }
]
```

---

### GET `/api/v1/documents/{document_id}`

Obtém um documento específico por ID.

**Path Parameters:**
- `document_id` (string, UUID): ID do documento

**Response:** `200 OK`
```json
{
  "id": "uuid-do-documento",
  "domain_id": "uuid-do-dominio",
  "use_case": "chat-training",
  "filename": "documento.pdf",
  "original_filename": "documento.pdf",
  "s3_key": "documents/.../documento.pdf",
  "content_type": "application/pdf",
  "file_size": 1024000,
  "status": "processed",
  "metadata": {},
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Documento não encontrado

---

### POST `/api/v1/documents/{document_id}/process`

Processa um documento: extrai texto e cria segmentos.

**Path Parameters:**
- `document_id` (string, UUID): ID do documento

**Request Body:**
```json
{
  "segment_type": "paragraph",
  "segment_config": {
    "max_length": 500,
    "overlap": 50
  }
}
```

**Campos:**
- `segment_type` (string, obrigatório): Tipo de segmento a criar
  - Valores possíveis: `paragraph`, `clause`, `chat_message`, `faq`, `crm_record`
- `segment_config` (object, opcional): Configurações de segmentação
  - Exemplo: `{"max_length": 500, "overlap": 50}`

**Response:** `202 Accepted`
```json
{
  "status": "processing",
  "version_id": "uuid-da-versao"
}
```

**Nota:** Este endpoint retorna imediatamente. O processamento acontece em background. Verifique o status do documento via GET `/api/v1/documents/{document_id}`.

**Erros:**
- `404`: Documento não encontrado
- `422`: Tipo de segmento inválido ou documento já processado

---

## Segments

Visualização e exploração de segmentos de texto extraídos.

### GET `/api/v1/segments`

Lista segmentos com filtros opcionais.

**Query Parameters (todos opcionais):**
- `domain_id` (string): Filtrar por domínio
- `document_id` (string): Filtrar por documento
- `use_case` (string): Filtrar por caso de uso
- `segment_type` (string): Filtrar por tipo de segmento

**Exemplo:**
```
GET /api/v1/segments?domain_id=uuid&segment_type=paragraph&document_id=uuid-doc
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-segmento",
    "domain_id": "uuid-do-dominio",
    "document_id": "uuid-do-documento",
    "document_version_id": "uuid-versao",
    "use_case": "chat-training",
    "segment_type": "paragraph",
    "content": "Texto completo do segmento...",
    "position": 0,
    "metadata": {},
    "created_at": "2024-01-04T22:27:51Z"
  }
]
```

---

### GET `/api/v1/segments/{segment_id}`

Obtém um segmento específico por ID.

**Path Parameters:**
- `segment_id` (string, UUID): ID do segmento

**Response:** `200 OK`
```json
{
  "id": "uuid-segmento",
  "domain_id": "uuid-do-dominio",
  "document_id": "uuid-do-documento",
  "document_version_id": "uuid-versao",
  "use_case": "chat-training",
  "segment_type": "paragraph",
  "content": "Texto completo do segmento...",
  "position": 0,
  "metadata": {},
  "created_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Segmento não encontrado

---

## Templates

Gerenciamento de templates de geração de prompts.

### POST `/api/v1/templates`

Cria um novo template de geração.

**Request Body:**
```json
{
  "domain_id": "uuid-do-dominio",
  "use_case": "chat-training",
  "name": "Template Chat Básico",
  "system_prompt": "Você é um assistente útil e prestativo.",
  "user_prompt_template": "Baseado no seguinte contexto: {content}\n\nGere uma resposta adequada.",
  "target_model_family": "llama",
  "config": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**Campos:**
- `domain_id` (string, obrigatório): ID do domínio
- `use_case` (string, opcional, max 100): Caso de uso
- `name` (string, obrigatório, 1-100 caracteres): Nome do template
- `system_prompt` (string, obrigatório, min 1): Prompt do sistema
- `user_prompt_template` (string, obrigatório, min 1): Template do prompt do usuário (deve conter `{content}`)
- `target_model_family` (string, opcional): Família do modelo (ex: "llama", "qwen", "gpt")
- `config` (object, opcional): Configurações adicionais

**Response:** `201 Created`
```json
{
  "id": "uuid-do-template",
  "domain_id": "uuid-do-dominio",
  "use_case": "chat-training",
  "name": "Template Chat Básico",
  "system_prompt": "Você é um assistente útil e prestativo.",
  "user_prompt_template": "Baseado no seguinte contexto: {content}\n\nGere uma resposta adequada.",
  "target_model_family": "llama",
  "config": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "is_active": true,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

---

### GET `/api/v1/templates`

Lista templates ativos.

**Query Parameters (opcionais):**
- `domain_id` (string): Filtrar por domínio
- `use_case` (string): Filtrar por caso de uso

**Exemplo:**
```
GET /api/v1/templates?domain_id=uuid&use_case=chat-training
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-template",
    "domain_id": "uuid-do-dominio",
    "use_case": "chat-training",
    "name": "Template Chat Básico",
    "system_prompt": "...",
    "user_prompt_template": "...",
    "target_model_family": "llama",
    "config": {},
    "is_active": true,
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:27:51Z"
  }
]
```

**Nota:** Apenas templates com `is_active: true` são retornados.

---

### GET `/api/v1/templates/{template_id}`

Obtém um template específico por ID.

**Path Parameters:**
- `template_id` (string, UUID): ID do template

**Response:** `200 OK`
```json
{
  "id": "uuid-do-template",
  "domain_id": "uuid-do-dominio",
  "use_case": "chat-training",
  "name": "Template Chat Básico",
  "system_prompt": "...",
  "user_prompt_template": "...",
  "target_model_family": "llama",
  "config": {},
  "is_active": true,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Template não encontrado

---

## Datasets

Gerenciamento de datasets de treinamento e geração sintética.

### POST `/api/v1/datasets`

Cria um novo dataset.

**Request Body:**
```json
{
  "domain_id": "uuid-do-dominio",
  "template_id": "uuid-do-template",
  "use_case": "chat-training",
  "name": "Dataset Chat VR 2024",
  "description": "Dataset para treinamento de chat",
  "provider": "openai",
  "target_model_family": "llama",
  "generation_config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "segment_filter": {
    "segment_type": "paragraph",
    "domain_id": "uuid-do-dominio"
  }
}
```

**Campos:**
- `domain_id` (string, obrigatório): ID do domínio
- `template_id` (string, opcional): ID do template de geração
- `use_case` (string, opcional, max 100): Caso de uso
- `name` (string, obrigatório, 1-200 caracteres): Nome do dataset
- `description` (string, opcional): Descrição
- `provider` (string, obrigatório): Provider LLM (`openai`, `gemini`, `together`)
- `target_model_family` (string, opcional): Família do modelo alvo
- `generation_config` (object, opcional): Configurações de geração
- `segment_filter` (object, opcional): Filtros para seleção de segmentos

**Response:** `201 Created`
```json
{
  "id": "uuid-do-dataset",
  "domain_id": "uuid-do-dominio",
  "template_id": "uuid-do-template",
  "use_case": "chat-training",
  "name": "Dataset Chat VR 2024",
  "description": "Dataset para treinamento de chat",
  "provider": "openai",
  "target_model_family": "llama",
  "status": "draft",
  "version": 1,
  "generation_config": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "segment_filter": {
    "segment_type": "paragraph"
  },
  "total_items": 0,
  "approved_items": 0,
  "rejected_items": 0,
  "pending_items": 0,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Status Possíveis:**
- `draft`: Dataset criado, aguardando geração
- `generating`: Geração de items em andamento
- `ready`: Pronto para exportação
- `archived`: Arquivado

---

### GET `/api/v1/datasets`

Lista todos os datasets.

**Query Parameters:**
- `domain_id` (string, opcional): Filtrar por domínio

**Exemplo:**
```
GET /api/v1/datasets?domain_id=uuid-do-dominio
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-dataset",
    "domain_id": "uuid-do-dominio",
    "template_id": "uuid-template",
    "use_case": "chat-training",
    "name": "Dataset Chat VR 2024",
    "description": "...",
    "provider": "openai",
    "target_model_family": "llama",
    "status": "ready",
    "version": 1,
    "generation_config": {},
    "segment_filter": {},
    "total_items": 100,
    "approved_items": 85,
    "rejected_items": 5,
    "pending_items": 10,
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:27:51Z"
  }
]
```

---

### GET `/api/v1/datasets/{dataset_id}`

Obtém um dataset específico por ID.

**Path Parameters:**
- `dataset_id` (string, UUID): ID do dataset

**Response:** `200 OK`
```json
{
  "id": "uuid-do-dataset",
  "domain_id": "uuid-do-dominio",
  "template_id": "uuid-do-template",
  "use_case": "chat-training",
  "name": "Dataset Chat VR 2024",
  "description": "...",
  "provider": "openai",
  "target_model_family": "llama",
  "status": "ready",
  "version": 1,
  "generation_config": {},
  "segment_filter": {},
  "total_items": 100,
  "approved_items": 85,
  "rejected_items": 5,
  "pending_items": 10,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Dataset não encontrado

---

### POST `/api/v1/datasets/generate`

Gera items sintéticos para um dataset.

**Request Body:**
```json
{
  "dataset_id": "uuid-do-dataset",
  "segment_ids": ["uuid-seg1", "uuid-seg2"],
  "max_items": 100,
  "batch_size": 10
}
```

**Campos:**
- `dataset_id` (string, obrigatório): ID do dataset
- `segment_ids` (array[string], opcional): IDs específicos de segmentos a usar. Se não fornecido, usa todos os segmentos que correspondem ao `segment_filter` do dataset
- `max_items` (integer, opcional, 1-10000): Número máximo de items a gerar
- `batch_size` (integer, opcional, default: 10, 1-100): Tamanho do lote para processamento

**Response:** `202 Accepted`
```json
{
  "status": "generating",
  "items_created": 0
}
```

**Nota:** Este endpoint retorna imediatamente. A geração acontece em background. O status do dataset será atualizado para `generating` e depois para `ready` quando concluído.

**Erros:**
- `404`: Dataset não encontrado
- `422`: Parâmetros inválidos (ex: max_items fora do range)

---

## Review

Revisão humana de items do dataset (Human-in-the-loop).

### GET `/api/v1/dataset/review/pending`

Lista items pendentes de revisão.

**Query Parameters:**
- `dataset_id` (string, opcional): Filtrar por dataset específico

**Exemplo:**
```
GET /api/v1/dataset/review/pending?dataset_id=uuid-do-dataset
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-item",
    "dataset_id": "uuid-do-dataset",
    "dataset_name": "Dataset Chat VR 2024",
    "instruction": "Responda à pergunta do usuário",
    "input_text": "Qual é a capital do Brasil?",
    "ideal_response": "A capital do Brasil é Brasília.",
    "bad_response": "Rio de Janeiro",
    "explanation": "Resposta precisa e direta",
    "quality_score": 0.95,
    "quality_flags": {
      "length_ok": true,
      "coherence_ok": true
    },
    "created_at": "2024-01-04T22:27:51Z"
  }
]
```

---

### POST `/api/v1/dataset/review/{item_id}/approve`

Aprova um item do dataset.

**Path Parameters:**
- `item_id` (string, UUID): ID do item do dataset

**Request Body:**
```json
{
  "reviewer_id": "user-123",
  "justification": "Item aprovado após revisão"
}
```

**Campos:**
- `reviewer_id` (string, opcional, max 100): Identificador do revisor
- `justification` (string, opcional): Justificativa da aprovação

**Response:** `200 OK`
```json
{
  "id": "uuid-review",
  "dataset_item_id": "uuid-item",
  "action": "approve",
  "reviewer_id": "user-123",
  "justification": "Item aprovado após revisão",
  "previous_values": null,
  "new_values": null,
  "created_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Item não encontrado

---

### POST `/api/v1/dataset/review/{item_id}/reject`

Rejeita um item do dataset.

**Path Parameters:**
- `item_id` (string, UUID): ID do item do dataset

**Request Body:**
```json
{
  "reviewer_id": "user-123",
  "justification": "Resposta incorreta ou de baixa qualidade"
}
```

**Campos:**
- `reviewer_id` (string, opcional, max 100): Identificador do revisor
- `justification` (string, obrigatório, min 1): Motivo da rejeição

**Response:** `200 OK`
```json
{
  "id": "uuid-review",
  "dataset_item_id": "uuid-item",
  "action": "reject",
  "reviewer_id": "user-123",
  "justification": "Resposta incorreta ou de baixa qualidade",
  "previous_values": null,
  "new_values": null,
  "created_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Item não encontrado
- `422`: Justificativa obrigatória não fornecida

---

### POST `/api/v1/dataset/review/{item_id}/edit`

Edita um item do dataset.

**Path Parameters:**
- `item_id` (string, UUID): ID do item do dataset

**Request Body:**
```json
{
  "reviewer_id": "user-123",
  "instruction": "Instrução editada",
  "input_text": "Input editado",
  "ideal_response": "Resposta ideal editada",
  "bad_response": "Resposta ruim editada",
  "explanation": "Explicação editada",
  "justification": "Correções necessárias para melhorar qualidade"
}
```

**Campos (todos opcionais, mas pelo menos um deve ser fornecido):**
- `reviewer_id` (string, max 100): Identificador do revisor
- `instruction` (string): Nova instrução
- `input_text` (string): Novo input
- `ideal_response` (string): Nova resposta ideal
- `bad_response` (string): Nova resposta ruim
- `explanation` (string): Nova explicação
- `justification` (string): Justificativa da edição

**Response:** `200 OK`
```json
{
  "id": "uuid-review",
  "dataset_item_id": "uuid-item",
  "action": "edit",
  "reviewer_id": "user-123",
  "justification": "Correções necessárias",
  "previous_values": {
    "instruction": "Instrução antiga",
    "ideal_response": "Resposta antiga"
  },
  "new_values": {
    "instruction": "Instrução editada",
    "ideal_response": "Resposta ideal editada"
  },
  "created_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Item não encontrado

---

### GET `/api/v1/dataset/review/{item_id}/history`

Obtém o histórico de revisões de um item.

**Path Parameters:**
- `item_id` (string, UUID): ID do item do dataset

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-review-1",
    "dataset_item_id": "uuid-item",
    "action": "approve",
    "reviewer_id": "user-123",
    "justification": "Aprovado",
    "previous_values": null,
    "new_values": null,
    "created_at": "2024-01-04T22:27:51Z"
  },
  {
    "id": "uuid-review-2",
    "dataset_item_id": "uuid-item",
    "action": "edit",
    "reviewer_id": "user-456",
    "justification": "Correção",
    "previous_values": {...},
    "new_values": {...},
    "created_at": "2024-01-04T22:28:00Z"
  }
]
```

**Nota:** Histórico ordenado por data de criação (mais antigo primeiro).

---

## Export

Exportação de datasets para formato JSONL.

### POST `/api/v1/datasets/{dataset_id}/export`

Exporta um dataset para JSONL.

**Path Parameters:**
- `dataset_id` (string, UUID): ID do dataset

**Request Body:**
```json
{
  "format": "jsonl",
  "approved_only": true,
  "filters": {
    "min_quality_score": 0.8
  }
}
```

**Campos:**
- `format` (string, opcional, default: `jsonl`): Formato de export (`jsonl`, `json`, `csv`)
- `approved_only` (boolean, opcional, default: `true`): Exportar apenas items aprovados
- `filters` (object, opcional): Filtros adicionais
  - Exemplo: `{"min_quality_score": 0.8}`

**Response:** `200 OK`
```json
{
  "id": "uuid-export",
  "dataset_id": "uuid-do-dataset",
  "export_version": 1,
  "format": "jsonl",
  "s3_key": "exports/uuid-do-dataset/v1/dataset.jsonl",
  "status": "completed",
  "item_count": 85,
  "filters_applied": {
    "approved_only": true,
    "min_quality_score": 0.8
  },
  "download_url": "https://s3.amazonaws.com/bucket/exports/...?signature=...",
  "created_at": "2024-01-04T22:27:51Z"
}
```

**Status Possíveis:**
- `pending`: Export iniciado
- `processing`: Processando
- `completed`: Concluído
- `failed`: Falhou

**Nota:** O `download_url` é uma URL pré-assinada do S3 válida por tempo limitado (geralmente 1 hora).

**Erros:**
- `404`: Dataset não encontrado

---

### GET `/api/v1/datasets/{dataset_id}/exports`

Lista todos os exports de um dataset.

**Path Parameters:**
- `dataset_id` (string, UUID): ID do dataset

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-export-1",
    "dataset_id": "uuid-do-dataset",
    "export_version": 1,
    "format": "jsonl",
    "s3_key": "exports/.../v1/dataset.jsonl",
    "status": "completed",
    "item_count": 85,
    "filters_applied": {},
    "download_url": null,
    "created_at": "2024-01-04T22:27:51Z"
  },
  {
    "id": "uuid-export-2",
    "dataset_id": "uuid-do-dataset",
    "export_version": 2,
    "format": "jsonl",
    "s3_key": "exports/.../v2/dataset.jsonl",
    "status": "completed",
    "item_count": 90,
    "filters_applied": {},
    "download_url": null,
    "created_at": "2024-01-04T22:28:00Z"
  }
]
```

**Nota:** `download_url` não é incluído na listagem. Use `GET /api/v1/datasets/exports/{export_id}/download` para obter URL atualizada.

---

### GET `/api/v1/datasets/exports/{export_id}/download`

Obtém URL de download atualizada para um export.

**Path Parameters:**
- `export_id` (string, UUID): ID do export

**Response:** `200 OK`
```json
{
  "download_url": "https://s3.amazonaws.com/bucket/exports/...?signature=..."
}
```

**Erros:**
- `404`: Export não encontrado

---

## Models

Registro e gerenciamento de modelos de IA.

### POST `/api/v1/models`

Registra um novo modelo.

**Request Body:**
```json
{
  "domain_id": "uuid-do-dominio",
  "name": "VR Chat Fine-tuned v1",
  "base_model": "llama-3.1-8b-instruct",
  "provider": "together",
  "model_family": "llama",
  "version": "1.0",
  "config": {
    "max_tokens": 4096
  },
  "capabilities": {
    "supports_functions": true,
    "supports_vision": false
  }
}
```

**Campos:**
- `domain_id` (string, opcional): ID do domínio associado
- `name` (string, obrigatório, 1-200 caracteres): Nome único do modelo
- `base_model` (string, obrigatório): Identificador do modelo base (ex: "llama-3.1-8b-instruct")
- `provider` (string, obrigatório): Provider do modelo (`openai`, `together`, `huggingface`, etc.)
- `model_family` (string, opcional): Família do modelo (ex: "llama", "qwen", "gpt")
- `version` (string, opcional): Versão do modelo (ex: "1.0", "fine-tuned-v2")
- `config` (object, opcional): Configurações do modelo
- `capabilities` (object, opcional): Capacidades do modelo

**Response:** `201 Created`
```json
{
  "id": "uuid-do-modelo",
  "domain_id": "uuid-do-dominio",
  "name": "VR Chat Fine-tuned v1",
  "base_model": "llama-3.1-8b-instruct",
  "provider": "together",
  "model_family": "llama",
  "version": "1.0",
  "status": "registered",
  "config": {
    "max_tokens": 4096
  },
  "capabilities": {
    "supports_functions": true,
    "supports_vision": false
  },
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Status Possíveis:**
- `registered`: Modelo registrado
- `training`: Em treinamento
- `deployed`: Deployado e disponível
- `archived`: Arquivado

---

### GET `/api/v1/models`

Lista todos os modelos.

**Query Parameters (opcionais):**
- `domain_id` (string): Filtrar por domínio
- `provider` (string): Filtrar por provider

**Exemplo:**
```
GET /api/v1/models?domain_id=uuid&provider=together
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-modelo",
    "domain_id": "uuid-do-dominio",
    "name": "VR Chat Fine-tuned v1",
    "base_model": "llama-3.1-8b-instruct",
    "provider": "together",
    "model_family": "llama",
    "version": "1.0",
    "status": "deployed",
    "config": {},
    "capabilities": {},
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:27:51Z"
  }
]
```

---

### GET `/api/v1/models/{model_id}`

Obtém um modelo específico por ID.

**Path Parameters:**
- `model_id` (string, UUID): ID do modelo

**Response:** `200 OK`
```json
{
  "id": "uuid-do-modelo",
  "domain_id": "uuid-do-dominio",
  "name": "VR Chat Fine-tuned v1",
  "base_model": "llama-3.1-8b-instruct",
  "provider": "together",
  "model_family": "llama",
  "version": "1.0",
  "status": "deployed",
  "config": {},
  "capabilities": {},
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Erros:**
- `404`: Modelo não encontrado

---

## Training Jobs

Gerenciamento de jobs de treinamento de modelos.

### POST `/api/v1/training-jobs`

Cria um novo job de treinamento.

**Request Body:**
```json
{
  "model_id": "uuid-do-modelo",
  "dataset_id": "uuid-do-dataset",
  "dataset_export_id": "uuid-do-export",
  "provider": "together",
  "hyperparameters": {
    "learning_rate": 2e-5,
    "epochs": 3,
    "batch_size": 8,
    "warmup_steps": 100
  }
}
```

**Campos:**
- `model_id` (string, obrigatório): ID do modelo a ser treinado
- `dataset_id` (string, obrigatório): ID do dataset de treinamento
- `dataset_export_id` (string, opcional): ID do export específico a usar. Se não fornecido, usa o export mais recente do dataset
- `provider` (string, obrigatório): Provider de treinamento (`together`, `huggingface`, etc.)
- `hyperparameters` (object, opcional): Hiperparâmetros de treinamento
  - Exemplo: `{"learning_rate": 2e-5, "epochs": 3, "batch_size": 8}`

**Response:** `201 Created`
```json
{
  "id": "uuid-do-job",
  "model_id": "uuid-do-modelo",
  "dataset_id": "uuid-do-dataset",
  "dataset_export_id": "uuid-do-export",
  "status": "pending",
  "provider": "together",
  "external_job_id": null,
  "hyperparameters": {
    "learning_rate": 2e-5,
    "epochs": 3,
    "batch_size": 8
  },
  "metrics": {},
  "error_message": null,
  "started_at": null,
  "completed_at": null,
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T22:27:51Z"
}
```

**Status Possíveis:**
- `pending`: Job criado, aguardando início
- `running`: Treinamento em andamento
- `completed`: Treinamento concluído com sucesso
- `failed`: Falha no treinamento
- `cancelled`: Cancelado

**Erros:**
- `404`: Modelo ou dataset não encontrado

---

### GET `/api/v1/training-jobs`

Lista todos os jobs de treinamento.

**Query Parameters (opcionais):**
- `model_id` (string): Filtrar por modelo
- `status` (string): Filtrar por status

**Exemplo:**
```
GET /api/v1/training-jobs?model_id=uuid&status=running
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid-job",
    "model_id": "uuid-do-modelo",
    "dataset_id": "uuid-do-dataset",
    "dataset_export_id": "uuid-do-export",
    "status": "running",
    "provider": "together",
    "external_job_id": "together-job-123",
    "hyperparameters": {
      "learning_rate": 2e-5,
      "epochs": 3
    },
    "metrics": {
      "loss": 0.5,
      "epoch": 2
    },
    "error_message": null,
    "started_at": "2024-01-04T22:27:51Z",
    "completed_at": null,
    "created_at": "2024-01-04T22:27:51Z",
    "updated_at": "2024-01-04T22:28:00Z"
  }
]
```

---

### GET `/api/v1/training-jobs/{job_id}`

Obtém um job específico por ID.

**Path Parameters:**
- `job_id` (string, UUID): ID do job

**Response:** `200 OK`
```json
{
  "id": "uuid-do-job",
  "model_id": "uuid-do-modelo",
  "dataset_id": "uuid-do-dataset",
  "dataset_export_id": "uuid-do-export",
  "status": "completed",
  "provider": "together",
  "external_job_id": "together-job-123",
  "hyperparameters": {
    "learning_rate": 2e-5,
    "epochs": 3
  },
  "metrics": {
    "final_loss": 0.3,
    "training_time": 3600
  },
  "error_message": null,
  "started_at": "2024-01-04T22:27:51Z",
  "completed_at": "2024-01-04T23:27:51Z",
  "created_at": "2024-01-04T22:27:51Z",
  "updated_at": "2024-01-04T23:27:51Z"
}
```

**Erros:**
- `404`: Job não encontrado

---

## Exemplos de Uso Completo

### Fluxo Completo: Upload → Processamento → Geração → Revisão → Export

#### 1. Criar Domínio
```http
POST /api/v1/domains
Content-Type: application/json

{
  "name": "VR Chat",
  "slug": "vr-chat",
  "description": "IA conversacional"
}
```

#### 2. Upload de Documento
```http
POST /api/v1/documents/upload?domain_id=uuid-do-dominio&use_case=chat-training
Content-Type: multipart/form-data

file: [arquivo.pdf]
```

#### 3. Processar Documento
```http
POST /api/v1/documents/uuid-do-documento/process
Content-Type: application/json

{
  "segment_type": "paragraph",
  "segment_config": {
    "max_length": 500
  }
}
```

#### 4. Criar Template
```http
POST /api/v1/templates
Content-Type: application/json

{
  "domain_id": "uuid-do-dominio",
  "name": "Template Chat",
  "system_prompt": "Você é um assistente útil.",
  "user_prompt_template": "Contexto: {content}\n\nResponda:"
}
```

#### 5. Criar Dataset
```http
POST /api/v1/datasets
Content-Type: application/json

{
  "domain_id": "uuid-do-dominio",
  "template_id": "uuid-do-template",
  "name": "Dataset Chat",
  "provider": "openai",
  "generation_config": {
    "model": "gpt-4",
    "temperature": 0.7
  }
}
```

#### 6. Gerar Items
```http
POST /api/v1/datasets/generate
Content-Type: application/json

{
  "dataset_id": "uuid-do-dataset",
  "max_items": 100,
  "batch_size": 10
}
```

#### 7. Listar Pendentes de Revisão
```http
GET /api/v1/dataset/review/pending?dataset_id=uuid-do-dataset
```

#### 8. Aprovar Item
```http
POST /api/v1/dataset/review/uuid-item/approve
Content-Type: application/json

{
  "reviewer_id": "user-123",
  "justification": "Aprovado"
}
```

#### 9. Exportar Dataset
```http
POST /api/v1/datasets/uuid-do-dataset/export
Content-Type: application/json

{
  "format": "jsonl",
  "approved_only": true
}
```

#### 10. Download do Export
```http
GET /api/v1/datasets/exports/uuid-do-export/download
```

---

## Notas Importantes

### Requisições HTTP Válidas

**IMPORTANTE:** O backend detecta requisições HTTP inválidas ou malformadas. Certifique-se de seguir estas diretrizes:

1. **Headers Obrigatórios:**
   ```http
   Content-Type: application/json
   Accept: application/json
   ```
   Exceção: Upload de arquivos usa `multipart/form-data`

2. **Métodos HTTP Corretos:**
   - `GET` para listar/obter recursos
   - `POST` para criar recursos
   - `PUT` para atualizar recursos
   - `DELETE` para deletar recursos (quando implementado)

3. **URLs Completas:**
   - Use URLs completas: `https://forge-server.grupo-vr.com/api/v1/domains`
   - Não use URLs relativas sem o protocolo correto
   - **Não inclua a porta** na URL pública (o proxy reverso gerencia isso)
   - Apenas para desenvolvimento local use `http://localhost:8000`

4. **Body JSON Válido:**
   - Sempre envie JSON válido quando usar `Content-Type: application/json`
   - Não envie strings vazias ou dados malformados
   - Valide o JSON antes de enviar

5. **Query Parameters:**
   - Use query parameters para filtros: `?domain_id=xxx&use_case=yyy`
   - Não inclua query parameters no body da requisição

### Problemas Comuns e Soluções

**Erro: "Invalid HTTP request received"**
- **Causa:** Requisição HTTP malformada ou headers incorretos
- **Solução:** 
  - Verifique se está usando o método HTTP correto
  - Certifique-se de que os headers estão corretos
  - Valide que o body JSON está bem formado
  - Verifique se a URL está completa e correta

**Erro: 404 Not Found**
- **Causa:** Rota não encontrada
- **Solução:**
  - Verifique se está usando o prefixo correto: `/api/v1/`
  - Confirme que a rota existe na documentação
  - Verifique se não há erros de digitação na URL

**Erro: 422 Validation Error**
- **Causa:** Dados inválidos no body da requisição
- **Solução:**
  - Verifique os campos obrigatórios
  - Confirme os tipos de dados (strings, números, etc.)
  - Valide UUIDs se necessário

### Upload de Arquivos

- **Tipos Suportados:** PDF, DOCX, TXT
- **Content-Type:** `multipart/form-data`
- **Limite de Tamanho:** Configurável no servidor (padrão: sem limite)
- **Parâmetros:** `domain_id` e `use_case` devem ser enviados como query parameters, não no body
- **Exemplo Correto:**
  ```javascript
  const formData = new FormData();
  formData.append('file', fileBlob);
  
  fetch('https://forge-server.grupo-vr.com/api/v1/documents/upload?domain_id=xxx&use_case=yyy', {
    method: 'POST',
    body: formData
  });
  ```

### Processamento Assíncrono

Os seguintes endpoints retornam `202 Accepted` e processam em background:
- `POST /api/v1/documents/{id}/process` - Processamento de documento
- `POST /api/v1/datasets/generate` - Geração de items sintéticos

Para verificar o status:
- Documentos: `GET /api/v1/documents/{id}` (campo `status`)
- Datasets: `GET /api/v1/datasets/{id}` (campo `status`)

### Validações

- **UUIDs:** Todos os IDs devem ser UUIDs válidos
- **Strings:** Campos de string têm limites de tamanho (ver schemas)
- **Enums:** Alguns campos aceitam apenas valores específicos:
  - `provider`: `openai`, `gemini`, `together`
  - `status`: Varia por entidade (ver documentação de cada endpoint)
  - `segment_type`: `paragraph`, `clause`, `chat_message`, `faq`, `crm_record`

### Paginação

Atualmente, as listagens não têm paginação implementada. Todas as rotas `GET` que retornam arrays retornam todos os resultados. Paginação será adicionada em versões futuras.

### Rate Limiting

Rate limiting não está implementado ainda. Será adicionado em versões futuras.

## Guia Rápido de Integração Frontend

### Configuração Base

```javascript
// Configuração do Axios ou Fetch
const API_BASE_URL = 'https://forge-server.grupo-vr.com';

// Headers padrão
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};
```

### Exemplos de Requisições Corretas

**1. Listar Domínios:**
```javascript
fetch(`${API_BASE_URL}/api/v1/domains`, {
  method: 'GET',
  headers: defaultHeaders
});
```

**2. Criar Domínio:**
```javascript
fetch(`${API_BASE_URL}/api/v1/domains`, {
  method: 'POST',
  headers: defaultHeaders,
  body: JSON.stringify({
    name: 'VR Chat',
    slug: 'vr-chat',
    description: 'IA conversacional'
  })
});
```

**3. Upload de Documento:**
```javascript
const formData = new FormData();
formData.append('file', fileBlob);

fetch(`${API_BASE_URL}/api/v1/documents/upload?domain_id=${domainId}&use_case=chat-training`, {
  method: 'POST',
  body: formData
  // NÃO inclua Content-Type header - o browser define automaticamente para FormData
});
```

**4. Listar Segmentos com Filtros:**
```javascript
const params = new URLSearchParams({
  domain_id: 'xxx',
  segment_type: 'paragraph'
});

fetch(`${API_BASE_URL}/api/v1/segments?${params}`, {
  method: 'GET',
  headers: defaultHeaders
});
```

### Tratamento de Erros

```javascript
try {
  const response = await fetch(url, options);
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Erro:', error.error);
    console.error('Detalhes:', error.details);
    console.error('Request ID:', error.request_id);
    // Use o request_id para rastreamento
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('Erro de rede:', error);
  throw error;
}
```

### Checklist de Validação

Antes de fazer uma requisição, verifique:

- [ ] URL está completa e correta (inclui protocolo, host, porta e path)
- [ ] Método HTTP está correto (GET, POST, PUT, DELETE)
- [ ] Headers estão corretos (`Content-Type: application/json` para JSON)
- [ ] Body JSON está bem formado (se aplicável)
- [ ] Query parameters estão na URL, não no body
- [ ] Para uploads, está usando `FormData` sem header `Content-Type`
- [ ] UUIDs estão no formato correto
- [ ] Campos obrigatórios estão presentes

---

## Suporte

Para dúvidas ou problemas, consulte os logs do servidor usando o `X-Request-ID` retornado nas respostas.

