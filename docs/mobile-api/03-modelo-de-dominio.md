# 03 — Modelo de Domínio

Todas as entidades de negócio herdam de `BaseModel`:
- `id`: **UUID v4** (chave primária, imutável)
- `created_at`: `datetime` (default = momento da criação)
- `updated_at`: `datetime` (atualizado automaticamente)
- Ordenação padrão: `-created_at`

Entidades de turma também podem ter exclusão lógica (`SoftDeleteModel`), com
`deleted_at` (nulo = ativo). Registros "soft-deleted" são ocultados por padrão.

## 3.1 Diagrama de relacionamentos

```
                         ┌───────────────┐
                         │     User      │  (login por e-mail)
                         │  email, name, │
                         │  phone        │
                         └───────┬───────┘
                                 │ 1:1
                         ┌───────▼───────┐
                         │   Guardian    │  cpf, pix_key,
                         │ (Responsável) │  pix_holder_name,
                         └──┬────┬────┬──┘  address, notes
              ┌────────────┘    │    └─────────────┐
       (membro de)         (responsável por)   (cria/paga)
              │ M:N (via ClassMember)│                │
   ┌──────────▼─────────┐    ┌───────▼──────┐         │
   │    SchoolClass     │    │   Student    │◄────────┘
   │ name, school, year,│ 1:N│ name,        │ (guardian)
   │ invite_code,       │────│ birth_date,  │
   │ is_active          │    │ notes        │
   └─────┬──────────┬───┘    └──────────────┘
         │ 1:N      │ 1:N
         │          └──────────────┐
   ┌─────▼──────┐          ┌────────▼─────────┐
   │   Event    │          │ ClassInvitation  │
   │ title,type,│          │ email, token,    │
   │ date, ...  │          │ status, expires  │
   └──┬───┬───┬─┘          └──────────────────┘
      │   │   │ 1:N
      │   │   └──────────────────────┐
      │   │ 1:N                       │ 1:N
 ┌────▼──────┐  ┌──────────────┐  ┌──▼─────────────────┐
 │ EventItem │  │   Payment    │  │ EventParticipation │
 │ name,type,│  │ amount,      │  │ status,            │
 │ qty,price,│  │ receipt,     │  │ contribution,      │
 │ assigned  │  │ status       │  │ guests_count       │
 └───────────┘  └──────────────┘  └────────────────────┘

Suppliers (independente — não ligado a turma):
   ┌──────────────┐         ┌──────────────────┐
   │ Supplier     │         │ SupplierCategory │ (catálogo opcional)
   │ name, phone, │         │ name, icon       │
   │ whatsapp,... │         └──────────────────┘
   └──────────────┘
```

Cardinalidades em texto:
- `User (1) ←→ (1) Guardian`
- `Guardian (M) ←→ (M) SchoolClass` através de `ClassMember`
- `Guardian (1) → (N) Student`
- `SchoolClass (1) → (N) Student`
- `SchoolClass (1) → (N) Event`
- `SchoolClass (1) → (N) ClassInvitation`
- `Event (1) → (N) EventItem | Payment | EventParticipation`
- `Supplier` é independente (global, não vinculado a turma)

---

## 3.2 accounts

### User
Usuário de autenticação. **Login por e-mail** (não há username).

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | int (BigAuto) | PK (note: User **não** usa UUID; as demais entidades sim) |
| `email` | string(email) | **único**, obrigatório, é o `USERNAME_FIELD` |
| `first_name` | string(150) | obrigatório |
| `last_name` | string(150) | opcional |
| `phone` | string(20) | opcional |
| `is_active` | bool | default `true` |
| `is_staff` | bool | só admin do sistema |
| `date_joined` | datetime | automático |

Derivado: `full_name` = `"first_name last_name"`.

### Guardian (Responsável)
Perfil de domínio ligado 1:1 ao `User`. **É a identidade usada em todo o app.**

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `user` | FK→User | 1:1, cascade |
| `cpf` | string(14) | opcional, formato `000.000.000-00` |
| `pix_key` | string(100) | opcional, chave PIX para recebimentos |
| `pix_holder_name` | string(100) | opcional, nome exibido ao receber PIX |
| `address` | text | opcional |
| `notes` | text | opcional |

Derivados (via `user`): `email`, `phone`, `full_name`.

> Regra: ao registrar um usuário, **um `Guardian` é criado automaticamente**. Várias
> views também criam o Guardian sob demanda caso ainda não exista.

---

## 3.3 classes

### SchoolClass (Turma)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `name` | string(100) | obrigatório (ex.: "3º Ano A", "Maternal II") |
| `school` | string(200) | opcional |
| `year` | int | default = ano atual |
| `description` | text | opcional |
| `invite_code` | string(20) | **único, gerado automaticamente**, não editável |
| `is_active` | bool | default `true` |

Derivados: `member_count`, `student_count`, `active_events_count`.
Métodos: `regenerate_invite_code()`.

### ClassMember (Membro da Turma)
Vínculo responsável ↔ turma.

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `school_class` | FK→SchoolClass | cascade |
| `guardian` | FK→Guardian | cascade |
| `role` | enum | `admin` \| `member` (default `member`) |
| `joined_at` | datetime | automático |

Restrição: **único** por (`school_class`, `guardian`).
Derivado: `is_admin` (`role == admin`).

### Student (Aluno)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `name` | string(200) | obrigatório |
| `school_class` | FK→SchoolClass | cascade |
| `guardian` | FK→Guardian | cascade (dono do aluno) |
| `birth_date` | date | opcional |
| `notes` | text | opcional (alergias, restrições, etc.) |

### ClassInvitation (Convite)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `school_class` | FK→SchoolClass | cascade |
| `invited_by` | FK→Guardian | set null |
| `email` | string(email) | opcional (vazio = convite genérico) |
| `token` | string(64) | **único, gerado automaticamente** (`secrets.token_urlsafe(32)`) |
| `status` | enum | `pending` \| `accepted` \| `expired` \| `cancelled` |
| `expires_at` | datetime | default = criação + 7 dias |
| `accepted_at` | datetime | nulo até aceitar |
| `accepted_by` | FK→Guardian | nulo até aceitar |

Derivados: `is_expired`, `is_valid` (= `pending` e não expirado).
Método: `accept(guardian)` → cria `ClassMember` (role `member`) e marca como aceito.

---

## 3.4 events

### Event (Evento)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `school_class` | FK→SchoolClass | cascade |
| `created_by` | FK→Guardian | set null (quem criou) |
| `title` | string(200) | obrigatório |
| `description` | text | obrigatório |
| `event_type` | enum | `payment` \| `potluck` \| `presence` (default `payment`) |
| `event_date` | date | obrigatório |
| `location` | string(300) | opcional |
| `location_url` | url | opcional (Google Maps) |
| `budget` | decimal(10,2) | opcional (total a arrecadar) |
| `individual_amount` | decimal(10,2) | opcional (calculado se vazio) |
| `pix_key` | string(100) | opcional |
| `pix_holder_name` | string(100) | opcional |
| `responsible` | FK→Guardian | set null (responsável pela arrecadação) |
| `is_active` | bool | default `true` |
| `closed_at` | datetime | nulo até encerrar |

Derivados (calculados):
- `is_presence_event` — `event_type == presence`
- `requires_participation` — `event_type ∈ {potluck, presence}`
- `confirmed_participations` — participações confirmadas
- `total_collected` — soma dos pagamentos **confirmados**
- `total_pending` — `budget - total_collected` (0 se sem budget)
- `payment_progress_percentage` — `min(100, total_collected/budget*100)`
- `paid_students` / `pending_students` — alunos com pagamento confirmado/pendente
- `pending_participations_students` — alunos com participação pendente

Métodos:
- `calculate_individual_amount()` → `budget / student_count` (None se sem budget)
- `close()` → `is_active=false`, `closed_at=now`

### EventItem (Item do Evento)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `event` | FK→Event | cascade |
| `name` | string(200) | obrigatório |
| `description` | text | opcional |
| `item_type` | enum | `expense` (despesa) \| `contribution` (contribuição) — default `contribution` |
| `quantity` | int | default 1 |
| `unit_price` | decimal(10,2) | opcional |
| `assigned_to` | FK→Guardian | set null (quem "assumiu" o item) |
| `is_completed` | bool | default `false` |

Derivado: `total_price` = `unit_price * quantity` (None se sem preço).

### Payment (Pagamento)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `event` | FK→Event | cascade |
| `guardian` | FK→Guardian | cascade (pagador) |
| `amount` | decimal(10,2) | obrigatório |
| `receipt` | file | opcional; img/PDF, ≤10MB; salvo em `receipts/AAAA/MM/` |
| `notes` | text | opcional |
| `status` | enum | `pending` \| `confirmed` \| `rejected` (default `pending`) |
| `confirmed_by` | FK→Guardian | set null (quem confirmou) |
| `confirmed_at` | datetime | nulo até confirmar |

Derivado: `is_confirmed`.
Métodos: `confirm(confirmed_by)`, `reject()`.

### EventParticipation (Participação)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `event` | FK→Event | cascade |
| `guardian` | FK→Guardian | cascade |
| `status` | enum | `pending` \| `confirmed` \| `declined` (default `pending`) |
| `contribution` | string(300) | o que vai levar (potluck) |
| `guests_count` | int | default 1 (quantas pessoas — presença) |
| `notes` | text | opcional |
| `confirmed_at` | datetime | nulo até confirmar |

Restrição: **único** por (`event`, `guardian`).
Derivado: `is_confirmed`.
Métodos: `confirm(contribution, guests_count, notes)`, `decline(notes)`.

---

## 3.5 suppliers

### Supplier (Fornecedor)

| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | UUID | PK |
| `category` | string(100) | opcional, texto livre (ex.: "Costureira", "Buffet") |
| `name` | string(200) | obrigatório |
| `contact_name` | string(200) | opcional |
| `phone` | string(20) | obrigatório |
| `whatsapp` | string(20) | opcional |
| `email` | string(email) | opcional |
| `website` | url | opcional |
| `instagram` | string(100) | opcional (usuário sem `@`) |
| `address` | text | opcional |
| `maps_url` | url | opcional |
| `description` | text | opcional |
| `notes` | text | opcional (notas internas) |
| `rating` | int(1–5) | opcional |
| `is_recommended` | bool | default `false` |
| `is_active` | bool | default `true` |

Derivados (links prontos, devem ser expostos na API):
- `whatsapp_link` → `https://wa.me/55<digits>` (usa `whatsapp` ou `phone`)
- `instagram_link` → `https://instagram.com/<user>`
- `maps_link` → `maps_url` ou busca no Google Maps pelo `address`

### SupplierCategory (Categoria de Fornecedor)
Catálogo opcional (existe no modelo, mas a UI atual usa `Supplier.category` como
texto livre). Campos: `name`, `description`, `icon` (nome de ícone Material Design).

> Observação: hoje as categorias da listagem vêm de `Supplier.category` (distinct),
> **não** de `SupplierCategory`. A API deve expor `GET /suppliers/categories` baseada
> nos valores distintos de `category` (ver doc 06).

---

## 3.6 Enumerações (resumo)

| Enum | Valores (chave → rótulo pt-BR) |
|------|-------------------------------|
| `ClassMember.Role` | `admin` → Administrador · `member` → Membro |
| `ClassInvitation.Status` | `pending` → Pendente · `accepted` → Aceito · `expired` → Expirado · `cancelled` → Cancelado |
| `Event.EventType` | `payment` → Arrecadação · `potluck` → Lanche Partilhado · `presence` → Confirmação de Presença |
| `EventItem.ItemType` | `expense` → Despesa · `contribution` → Contribuição |
| `Payment.Status` | `pending` → Pendente · `confirmed` → Confirmado · `rejected` → Rejeitado |
| `EventParticipation.Status` | `pending` → Pendente · `confirmed` → Confirmado · `declined` → Recusado |

> O tipo `MIXED` de evento foi **removido** do sistema. Só existem 3 tipos.
> A API deve enviar a **chave** (em inglês) e, opcionalmente, um campo `*_display`
> com o rótulo pt-BR para a UI do app.
