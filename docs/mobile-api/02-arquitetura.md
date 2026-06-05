# 02 — Arquitetura

## 2.1 Arquitetura atual (web Django)

```
┌──────────────────────────────────────────────────────────────┐
│                        Cliente (Browser)                       │
│            Templates Django + Tailwind + crispy-forms          │
└───────────────────────────────┬──────────────────────────────┘
                                 │ HTML (server-side render)
                                 │ Sessão + Cookie + CSRF
┌───────────────────────────────▼──────────────────────────────┐
│                        Django 5.1 (WSGI)                       │
│                                                                │
│  config/                                                       │
│   ├─ settings/ (base, dev, prod)  ── python-decouple           │
│   └─ urls.py                                                   │
│                                                                │
│  apps/                                                         │
│   ├─ core      → BaseModel, PixService, EmailService, DI       │
│   ├─ accounts  → User (email), Guardian                        │
│   ├─ classes   → SchoolClass, ClassMember, Student, Invitation │
│   ├─ events    → Event, EventItem, Payment, Participation      │
│   ├─ suppliers → Supplier                                      │
│   └─ dashboard → estatísticas agregadas                        │
│                                                                │
│  Camadas: Views (CBV) → Forms → Models → Services              │
│  DI: dependency-injector (CoreContainer)                       │
└──────┬───────────────────────┬──────────────────┬────────────┘
       │                       │                  │
┌──────▼──────┐        ┌───────▼──────┐    ┌──────▼─────────┐
│ PostgreSQL  │        │ S3 / MinIO    │    │ SMTP (MailHog) │
│ 16+         │        │ (comprovantes)│    │ / e-mail prod  │
└─────────────┘        └──────────────┘    └────────────────┘
```

### Stack atual
- **Framework:** Django 5.1
- **Banco:** PostgreSQL 16+ (via `psycopg` + `dj-database-url`)
- **Admin:** Django Unfold
- **Forms/UI:** `crispy-forms` + `crispy-tailwind` + `widget-tweaks`
- **PIX:** `qrcode[pil]` + serviço próprio (`PixService`, EMV BR Code)
- **Imagens:** `Pillow`
- **DI:** `dependency-injector`
- **Storage:** `django-storages[s3]` + `boto3` (MinIO em dev, Cloudflare R2 em prod)
- **Config:** `python-decouple` (settings em 3 camadas: base/dev/prod)
- **Qualidade:** `ruff`, `pyright`, `pytest` + `factory-boy`, `pre-commit`

### Princípios de design seguidos
- **DDD** (organização por domínio/app), **SOLID**, **Object Calisthenics**.
- Modelos herdam de `BaseModel` (UUID + timestamps) e, quando aplicável, de
  `SoftDeleteModel` (exclusão lógica).
- Serviços injetados via container (`PixService`, `EmailService`).
- Otimização de queries (`select_related`/`prefetch_related`, evita N+1).

## 2.2 Arquitetura-alvo (API para o app Flutter)

A recomendação é **adicionar uma camada REST** ao mesmo backend Django, sem reescrever
o domínio. Reaproveita-se 100% dos modelos, regras e serviços existentes; muda-se apenas
a camada de entrega (de templates HTML para JSON).

```
┌───────────────────────────┐        ┌───────────────────────────┐
│      App Flutter           │        │   Web atual (templates)    │
│  (iOS / Android)           │        │   continua funcionando      │
└─────────────┬─────────────┘        └─────────────┬─────────────┘
              │ HTTPS + Bearer JWT                  │ Sessão/Cookie
              │ JSON / multipart                    │ HTML
              ▼                                      ▼
┌──────────────────────────────────────────────────────────────┐
│                         Django 5.1                            │
│  ┌───────────────────────────┐   ┌────────────────────────┐  │
│  │  API REST (DRF) — NOVO     │   │  Views server-side      │  │
│  │  /api/v1/...               │   │  (mantidas)             │  │
│  │  - Serializers             │   └────────────────────────┘  │
│  │  - ViewSets / APIViews     │                                │
│  │  - Permissions             │   ┌────────────────────────┐  │
│  │  - JWT (SimpleJWT)         │   │  Django Admin (Unfold)  │  │
│  │  - OpenAPI (spectacular)   │   └────────────────────────┘  │
│  └───────────────────────────┘                                │
│  ──────────────  Domínio compartilhado  ──────────────────    │
│  Models · Services (PixService, EmailService) · DI            │
└──────┬───────────────────────┬──────────────────┬────────────┘
       ▼                       ▼                  ▼
  PostgreSQL              S3 / R2            E-mail + (Push futuro)
```

### Bibliotecas recomendadas para a camada API
| Necessidade | Biblioteca sugerida | Observação |
|-------------|---------------------|-----------|
| REST framework | `djangorestframework` | ViewSets, serializers, permissions |
| Autenticação por token | `djangorestframework-simplejwt` | Access + refresh token |
| Documentação OpenAPI | `drf-spectacular` | Gera o `openapi.yaml`, alimenta o codegen Flutter |
| CORS (app/web) | `django-cors-headers` | Liberar origem do app/web em dev |
| Filtros/busca | `django-filter` | Para listas de fornecedores/eventos |
| Throttling | DRF nativo | Proteger login/registro |

### Por que JWT (e não sessão)?
A web atual usa **sessão + cookie + CSRF**, que funciona bem em browser, mas é
inconveniente para apps mobile. Para o Flutter, recomenda-se **JWT Bearer**:
- `POST /auth/login` → `access` (curta duração) + `refresh` (longa duração).
- O app guarda os tokens em armazenamento seguro (Keychain/Keystore via
  `flutter_secure_storage`).
- `POST /auth/refresh` renova o `access` sem novo login.
- Endpoints protegidos exigem `Authorization: Bearer <access>`.

Detalhes em [05-autenticacao-permissoes.md](./05-autenticacao-permissoes.md).

## 2.3 Camadas e responsabilidades (alvo)

| Camada | Responsabilidade | Onde |
|--------|------------------|------|
| **Serializer** | Validação de entrada/saída, formatação JSON | `apps/<app>/api/serializers.py` |
| **ViewSet/APIView** | Orquestração HTTP, paginação, status codes | `apps/<app>/api/views.py` |
| **Permission** | Autorização (admin de turma, criador, responsável) | `apps/<app>/api/permissions.py` |
| **Model** | Regras de domínio (já existem) | `apps/<app>/models.py` |
| **Service** | PIX, e-mail (já existem) | `apps/core/services/` |

> Importante: a lógica de negócio **já vive nos modelos** (`Event.calculate_individual_amount`,
> `Payment.confirm`, `ClassInvitation.accept`, `EventParticipation.confirm`, etc.).
> A camada API deve **chamar esses métodos**, não reimplementá-los.

## 2.4 Armazenamento de arquivos (comprovantes)

- Comprovantes (`Payment.receipt`) são salvos em `receipts/%Y/%m/` em storage
  S3-compatível (MinIO em dev, Cloudflare R2 em prod).
- O upload via API deve ser `multipart/form-data`.
- A resposta JSON do pagamento deve conter a **URL absoluta** do comprovante
  (`receipt_url`) para o app exibir.
- Validação atual (replicar na API): extensões `jpg, jpeg, png, gif, webp, pdf`;
  tamanho máximo **10 MB**.

## 2.5 Ambientes e configuração

Configuração via variáveis de ambiente (`python-decouple`). Settings em 3 camadas:
`config/settings/base.py` + `dev.py` + `prod.py`.

Variáveis-chave (ver `env.example` e README do projeto):
`SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`,
`PIX_KEY`, `PIX_MERCHANT_NAME`, `PIX_MERCHANT_CITY`,
`STORAGE_*` (S3), `EMAIL_*` (SMTP), `DEFAULT_FROM_EMAIL`.

Para o mobile, adicionar (sugestão):
`CORS_ALLOWED_ORIGINS`, `JWT_ACCESS_TOKEN_LIFETIME`, `JWT_REFRESH_TOKEN_LIFETIME`.

## 2.6 Versionamento da API

- Prefixo `/api/v1`. Mudanças incompatíveis → `/api/v2`.
- O `openapi.yaml` é a fonte de verdade do contrato; o app Flutter pode gerar
  models/clients a partir dele (ex.: `openapi-generator`, `swagger_dart_code_generator`
  ou `retrofit` + `json_serializable`).
