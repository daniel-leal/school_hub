# 06 — Referência da API REST

Especificação-alvo dos endpoints para o app Flutter. **Base URL:** `/api/v1`.
Todos os endpoints (exceto auth público) exigem `Authorization: Bearer <access>`.

> Esta é a **especificação a implementar** (camada DRF). Ao lado de cada grupo há a
> referência à rota/funcionalidade web equivalente de hoje. O contrato formal está em
> [openapi.yaml](./openapi.yaml).

## Convenções

- **Sucesso:** `200 OK` (leitura/ação), `201 Created` (criação), `204 No Content`
  (sem corpo).
- **Erros:** `400` validação, `401` não autenticado, `403` sem permissão,
  `404` não encontrado, `409` conflito (ex.: pagamento duplicado), `422` regra de negócio.
- **Formato de erro (sugerido):**
  ```json
  { "detail": "Mensagem legível", "code": "payment_already_exists", "fields": { "amount": ["Obrigatório."] } }
  ```
- **Paginação:** `?page=N` →
  ```json
  { "count": 42, "next": "...?page=3", "previous": "...?page=1", "results": [ ... ] }
  ```
- **Datas:** `event_date` = `YYYY-MM-DD`; timestamps = ISO-8601 UTC.
- **Dinheiro:** string decimal `"150.00"`.

---

## 1. Autenticação e perfil  · (web: `apps/accounts`)

### `POST /auth/register` — Cadastro
Cria `User` + `Guardian`. Equivale a `RegisterView`.

Request:
```json
{
  "email": "maria@email.com",
  "first_name": "Maria",
  "last_name": "Silva",
  "phone": "(11) 99999-0000",
  "password": "senhaForte123",
  "class_code": "ABC123XYZ0"
}
```
- `class_code` (opcional): se válido, entra na turma como `member` (RN-AC-04).

Response `201`:
```json
{
  "user": { "id": 1, "email": "maria@email.com", "first_name": "Maria",
            "last_name": "Silva", "phone": "(11) 99999-0000", "full_name": "Maria Silva" },
  "guardian_id": "9f1c...uuid",
  "joined_class": { "id": "uuid", "name": "3º Ano A" },
  "access": "jwt...", "refresh": "jwt..."
}
```

### `POST /auth/login`
Request: `{ "email": "...", "password": "..." }`
Response `200`: `{ "access": "jwt...", "refresh": "jwt..." }`

### `POST /auth/refresh`
Request: `{ "refresh": "jwt..." }` → Response `200`: `{ "access": "jwt..." }`

### `POST /auth/logout`
Request: `{ "refresh": "jwt..." }` → `204`. (Blacklist do refresh.)

### `POST /auth/password/change`
Request: `{ "old_password": "...", "new_password": "..." }` → `204`.
Equivale a `PasswordChangeView`.

### `GET /me` — Perfil
Response `200`:
```json
{
  "user": { "id": 1, "email": "maria@email.com", "first_name": "Maria",
            "last_name": "Silva", "phone": "(11) 99999-0000", "full_name": "Maria Silva" },
  "guardian": { "id": "uuid", "cpf": "000.000.000-00", "pix_key": "maria@email.com",
                "pix_holder_name": "Maria Silva", "address": "", "notes": "" }
}
```

### `PATCH /me` — Editar perfil
Atualiza campos de `User` e/ou `Guardian` numa só chamada (equivale a `ProfileUpdateView`):
```json
{
  "first_name": "Maria", "last_name": "Souza", "phone": "(11) 98888-0000",
  "cpf": "123.456.789-00", "pix_key": "11988880000",
  "pix_holder_name": "Maria Souza", "address": "Rua X, 10", "notes": ""
}
```

### `GET /me/pix` — Info de PIX  · (web: `GET /accounts/api/pix-info/` — único JSON existente hoje)
Response `200`:
```json
{ "pix_key": "maria@email.com", "pix_holder_name": "Maria Silva", "has_pix": true }
```
`pix_holder_name` cai para o nome completo do usuário se vazio (RN-AC-06).

---

## 2. Turmas  · (web: `apps/classes`)

### `GET /classes` — Minhas turmas (paginado)
Apenas turmas ativas das quais o responsável é membro (RN-CL-03).
Item:
```json
{
  "id": "uuid", "name": "3º Ano A", "school": "Escola Municipal", "year": 2026,
  "description": "", "invite_code": "ABC123XYZ0", "is_active": true,
  "member_count": 12, "student_count": 15, "active_events_count": 3,
  "my_role": "admin"
}
```

### `POST /classes` — Criar turma
Cria a turma e adiciona o criador como `admin` (RN-CL-02). `invite_code` gerado (RN-CL-01).
Request: `{ "name": "3º Ano A", "school": "Escola Municipal", "year": 2026, "description": "" }`
Response `201`: objeto da turma (com `invite_code` e `my_role: "admin"`).

### `GET /classes/{id}` — Detalhe
Equivale a `ClassDetailView`. Response:
```json
{
  "id": "uuid", "name": "3º Ano A", "school": "...", "year": 2026,
  "description": "", "invite_code": "ABC123XYZ0", "is_active": true,
  "member_count": 12, "student_count": 15, "active_events_count": 3,
  "is_member": true, "is_admin": true,
  "my_students": [ { "id": "uuid", "name": "João Silva", "birth_date": "2018-05-10" } ],
  "members": [
    { "id": "uuid", "guardian_id": "uuid", "full_name": "Maria Silva",
      "role": "admin", "joined_at": "2026-01-10T12:00:00Z" }
  ],
  "students": [
    { "id": "uuid", "name": "João Silva", "guardian_full_name": "Maria Silva",
      "birth_date": "2018-05-10" }
  ],
  "recent_events": [
    { "id": "uuid", "title": "Festa Junina", "event_type": "potluck",
      "event_date": "2026-06-20", "is_active": true }
  ]
}
```
> Nota de segurança: a API deve retornar 403/404 se o solicitante não for membro
> (ver doc 05, §5.5).

### `PATCH /classes/{id}` — Editar turma  *(somente admin)*
Campos: `name`, `school`, `year`, `description`.

### `POST /classes/{id}/regenerate-code` — Novo código  *(somente admin)*
Existe no modelo (`regenerate_invite_code`); expor como endpoint (RN-CL-08).
Response: `{ "invite_code": "NOVOCODIGO" }`.

### `POST /classes/join` — Entrar por código
Request: `{ "invite_code": "ABC123XYZ0" }`
- código inválido → `404`/`400`.
- entrou agora → `201` `{ "class": {...}, "created": true }`.
- já era membro → `200` `{ "class": {...}, "created": false }`.

### Alunos

#### `GET /classes/{id}/students` — Lista de alunos da turma
#### `POST /classes/{id}/students` — Cadastrar aluno
`guardian` = responsável logado; `school_class` = turma da rota (RN-ST-01).
Request: `{ "name": "João Silva", "birth_date": "2018-05-10", "notes": "Alergia a amendoim" }`
Response `201`: aluno criado.

#### `PATCH /students/{id}` — Editar aluno  *(só dono)*
#### `DELETE /students/{id}` — Excluir aluno  *(só dono)* → `204`

### Convites

#### `POST /classes/{id}/invitations` — Criar convite  *(admin)*
`invited_by` = responsável logado; `token`/`expires_at` automáticos (RN-IN-01/02).
Request: `{ "email": "novopai@email.com", "expires_at": "2026-07-01T00:00:00Z" }`
- `email` vazio = convite genérico; com e-mail → envia e-mail (RN-IN-04).
Response `201`:
```json
{ "id": "uuid", "token": "abc...", "email": "novopai@email.com",
  "status": "pending", "expires_at": "2026-07-01T00:00:00Z",
  "invite_url": "https://app/.../convite/abc..." }
```

#### `GET /invitations/{token}` — Dados do convite (público ou autenticado)
Permite a tela "você foi convidado para a turma X" antes de aceitar.
Response: `{ "token": "...", "school_class": { "id": "...", "name": "3º Ano A" }, "status": "pending", "is_valid": true, "expires_at": "..." }`

#### `POST /invitations/{token}/accept` — Aceitar convite
Cria/garante `ClassMember` (member) e marca aceito (RN-IN-05). Inválido → `422`.
Response: `{ "class": { "id": "...", "name": "3º Ano A" }, "membership_role": "member" }`

---

## 3. Eventos  · (web: `apps/events`)

### `GET /events` — Meus eventos (paginado)
Eventos ativos das turmas do responsável (RN-EV-05). Filtros sugeridos:
`?class_id=`, `?event_type=`, `?is_active=`.
Item:
```json
{
  "id": "uuid", "title": "Festa Junina", "event_type": "potluck",
  "event_type_display": "Lanche Partilhado",
  "event_date": "2026-06-20", "is_active": true,
  "school_class": { "id": "uuid", "name": "3º Ano A" },
  "created_by_name": "Maria Silva",
  "budget": null, "individual_amount": null,
  "payment_progress_percentage": 0, "requires_participation": true
}
```

### `POST /classes/{id}/events` — Criar evento
`created_by` e `responsible` = logado; calcula `individual_amount` se `budget` e vazio;
envia e-mail aos membros (RN-EV-02).
Request:
```json
{
  "title": "Lembrança Dia das Mães", "description": "Vaquinha p/ presente",
  "event_type": "payment", "event_date": "2026-05-08",
  "location": "Escola", "location_url": "https://maps.google.com/...",
  "budget": "300.00", "individual_amount": null,
  "pix_key": "maria@email.com", "pix_holder_name": "Maria Silva"
}
```
Response `201`: evento completo (ver detalhe abaixo).

### `GET /events/{id}` — Detalhe do evento
Equivale a `EventDetailView` (agrega itens, pagamentos, participações e permissões).
```json
{
  "id": "uuid", "title": "Lembrança Dia das Mães", "description": "...",
  "event_type": "payment", "event_type_display": "Arrecadação",
  "event_date": "2026-05-08", "location": "Escola",
  "location_url": "https://maps.google.com/...",
  "budget": "300.00", "individual_amount": "20.00",
  "pix_key": "maria@email.com", "pix_holder_name": "Maria Silva",
  "is_active": true, "closed_at": null,
  "school_class": { "id": "uuid", "name": "3º Ano A" },
  "created_by_name": "Maria Silva", "responsible_name": "Maria Silva",

  "requires_participation": false,
  "total_collected": "120.00", "total_pending": "180.00",
  "payment_progress_percentage": 40,

  "permissions": {
    "is_admin": true, "is_creator": true, "is_responsible": true,
    "can_edit": true, "can_confirm_payments": true
  },
  "my_payment": { "id": "uuid", "amount": "20.00", "status": "confirmed",
                  "receipt_url": "https://.../receipt.pdf" },
  "has_paid": true,
  "my_participation": null,
  "has_confirmed_participation": false,

  "items": [
    { "id": "uuid", "name": "Lembrancinhas", "description": "",
      "item_type": "contribution", "item_type_display": "Contribuição",
      "quantity": 30, "unit_price": "5.00", "total_price": "150.00",
      "assigned_to_name": "Ana", "is_completed": false }
  ],
  "expense_items": [ ... ], "contribution_items": [ ... ],

  "payments": [
    { "id": "uuid", "guardian_full_name": "Maria Silva",
      "student_names": ["João Silva"], "amount": "20.00",
      "status": "confirmed", "status_display": "Confirmado",
      "receipt_url": "https://.../r.pdf", "notes": "",
      "confirmed_by_name": "Maria Silva", "confirmed_at": "2026-05-01T10:00:00Z",
      "created_at": "2026-04-30T09:00:00Z" }
  ],
  "confirmed_payments": [ ... ], "pending_payments": [ ... ],

  "participations": [],
  "confirmed_participations": [], "pending_participations": []
}
```
> `payments[].student_names` vem do prefetch dos alunos do `guardian` naquela turma
> (a web mostra nome do responsável + filhos). Mantém-se na API.

### `PATCH /events/{id}` — Editar evento  *(can_edit)*
Mesmos campos do create. Recalcula `individual_amount` se `budget` mudar e estiver vazio.

### `POST /events/{id}/close` — Encerrar evento  *(can_edit)* → `200` evento atualizado (`is_active=false`).

### Itens do evento

#### `GET /events/{id}/items`
#### `POST /events/{id}/items` — Adicionar item *(can_edit)*
Request: `{ "name": "Bolo", "description": "", "item_type": "expense", "quantity": 1, "unit_price": "80.00" }`
#### `PATCH /items/{id}` — Editar item *(can_edit)*
#### `POST /items/{id}/assign` — Assumir item (qualquer membro) → define `assigned_to` = logado.
#### `POST /items/{id}/complete` — Concluir item → `is_completed=true`.

### Pagamentos

#### `GET /events/{id}/payments` — Lista de pagamentos do evento
#### `POST /events/{id}/payments` — Enviar pagamento  *(membro com aluno na turma)*
**`multipart/form-data`** (RN-PG-01/02/03/04):
- `amount` (string decimal) — obrigatório
- `receipt` (arquivo) — opcional; img/PDF ≤10MB
- `notes` (texto) — opcional

Respostas:
- `201`: pagamento criado (`status: pending`).
- `409`: já existe pagamento desse responsável no evento.
- `403`: responsável não tem aluno na turma.

> Dica para o app: para pré-preencher o valor, use
> `event.individual_amount × nº de alunos do responsável na turma`.

#### `POST /payments/{id}/confirm` — Confirmar  *(can_confirm_payments)*
`status=confirmed`, grava `confirmed_by/at`, envia e-mail (RN-PG-06). → `200`.
#### `POST /payments/{id}/reject` — Rejeitar  *(can_confirm_payments)*
`status=rejected`, envia e-mail (RN-PG-07). → `200`.

### PIX

#### `GET /events/{id}/pix` — Código + QR (JSON)
Equivale a `EventPixView`. Se sem `pix_key` → `400`/`404` (RN-PX-02).
```json
{
  "pix_key": "maria@email.com", "pix_holder_name": "Maria Silva",
  "amount": "20.00",
  "pix_code": "00020126...6304ABCD",
  "qr_code_base64": "iVBORw0KGgoAAA...",
  "qr_code_url": "/api/v1/events/{id}/qrcode"
}
```
#### `GET /events/{id}/qrcode` — Imagem PNG do QR
`Content-Type: image/png`. Sem `pix_key` → `400`.

### Participações (lanche partilhado / presença)

#### `GET /events/{id}/participations`
#### `POST /events/{id}/participations` — Confirmar participação
Só se `requires_participation` e responsável tiver aluno na turma (RN-PT-01/02).
`get_or_create` + `confirm` (RN-PT-03/06).
Request (potluck): `{ "contribution": "Pão de queijo", "notes": "" }` (`contribution` obrigatório)
Request (presence): `{ "guests_count": 3, "notes": "" }`
Response `200`/`201`: participação `confirmed`.
- `422` se evento não requer participação; `403` se sem aluno na turma.

#### `POST /events/{id}/participations/decline` — Recusar
Request: `{ "notes": "Não poderemos ir" }` → `status=declined` (RN-PT-07).
#### `POST /events/{id}/participations/cancel` — Cancelar confirmada
Só se estava `confirmed` → vira `declined` com nota "Cancelado pelo usuário" (RN-PT-08).

---

## 4. Fornecedores  · (web: `apps/suppliers`)

### `GET /suppliers` — Lista (paginado)
Apenas ativos; recomendados primeiro (RN-SP-01). Filtros: `?q=` (nome), `?category=`.
Item:
```json
{
  "id": "uuid", "category": "Buffet", "name": "Festas da Ana",
  "contact_name": "Ana", "phone": "(11) 99999-0000",
  "whatsapp": "(11) 99999-0000", "email": "", "website": "",
  "instagram": "festasdaana", "address": "Rua X, 10", "maps_url": "",
  "description": "Bolos e salgados", "rating": 5, "is_recommended": true,
  "whatsapp_link": "https://wa.me/5511999990000",
  "instagram_link": "https://instagram.com/festasdaana",
  "maps_link": "https://www.google.com/maps/search/?api=1&query=Rua%20X%2C%2010"
}
```

### `GET /suppliers/categories` — Categorias distintas
Valores distintos de `category` entre ativos (RN-SP-03).
Response: `{ "categories": ["Buffet", "Costureira", "Decorador"] }`

### `GET /suppliers/{id}` — Detalhe
### `POST /suppliers` — Cadastrar
### `PATCH /suppliers/{id}` — Editar
Campos: `category, name, contact_name, phone, whatsapp, email, website, instagram,
address, maps_url, description, notes`. (`notes` é interno; avaliar expor só ao autor.)

---

## 5. Dashboard  · (web: `apps/dashboard`)

### `GET /dashboard` — Visão geral do responsável
Equivale a `DashboardView` (RN-DB-*). Response:
```json
{
  "has_guardian": true,
  "totals": {
    "classes": 2, "students": 3, "events": 8, "active_events": 4,
    "total_payments": "540.00", "pending_payments_count": 1
  },
  "upcoming_events": [
    { "id": "uuid", "title": "Festa Junina", "event_type": "potluck",
      "event_date": "2026-06-20", "school_class_name": "3º Ano A" }
  ],
  "recent_payments": [
    { "id": "uuid", "event_title": "Dia das Mães", "amount": "20.00",
      "status": "confirmed", "created_at": "2026-05-01T09:00:00Z" }
  ],
  "monthly_expenses": {
    "labels": ["jan/26", "fev/26", "mar/26"],
    "data": [50.0, 0.0, 120.0]
  },
  "classes": [
    { "id": "uuid", "name": "3º Ano A", "events_total": 5, "students_total": 2 }
  ],
  "birthdays": [
    { "id": "uuid", "name": "João Silva", "birth_date": "2018-06-10",
      "school_class_name": "3º Ano A", "day": 10 }
  ],
  "today": "2026-06-05"
}
```

---

## 6. Mapa rota web → endpoint API

| Funcionalidade | Web (hoje) | API (alvo) |
|----------------|-----------|------------|
| Login | `accounts:login` | `POST /auth/login` |
| Logout | `accounts:logout` | `POST /auth/logout` |
| Cadastro | `accounts:register` | `POST /auth/register` |
| Alterar senha | `accounts:password_change` | `POST /auth/password/change` |
| Perfil (ver) | `accounts:profile` | `GET /me` |
| Perfil (editar) | `accounts:profile_update` | `PATCH /me` |
| PIX info | `accounts:pix_info` | `GET /me/pix` |
| Turmas (lista) | `classes:list` | `GET /classes` |
| Turma (criar) | `classes:create` | `POST /classes` |
| Turma (detalhe) | `classes:detail` | `GET /classes/{id}` |
| Turma (editar) | `classes:update` | `PATCH /classes/{id}` |
| Entrar por código | `classes:join` | `POST /classes/join` |
| Aluno (criar) | `classes:student_create` | `POST /classes/{id}/students` |
| Aluno (editar) | `classes:student_update` | `PATCH /students/{id}` |
| Aluno (excluir) | `classes:student_delete` | `DELETE /students/{id}` |
| Convite (criar) | `classes:create_invitation` | `POST /classes/{id}/invitations` |
| Convite (aceitar) | `classes:accept_invitation` | `POST /invitations/{token}/accept` |
| Eventos (lista) | `events:list` | `GET /events` |
| Evento (criar) | `events:create` | `POST /classes/{id}/events` |
| Evento (detalhe) | `events:detail` | `GET /events/{id}` |
| Evento (editar) | `events:update` | `PATCH /events/{id}` |
| Evento (encerrar) | `events:close` | `POST /events/{id}/close` |
| Item (criar) | `events:item_create` | `POST /events/{id}/items` |
| Item (editar) | `events:item_update` | `PATCH /items/{id}` |
| Item (assumir) | `events:item_assign` | `POST /items/{id}/assign` |
| Item (concluir) | `events:item_complete` | `POST /items/{id}/complete` |
| Pagamento (criar) | `events:payment_create` | `POST /events/{id}/payments` |
| Pagamento (confirmar) | `events:payment_confirm` | `POST /payments/{id}/confirm` |
| Pagamento (rejeitar) | `events:payment_reject` | `POST /payments/{id}/reject` |
| PIX (ver) | `events:pix` | `GET /events/{id}/pix` |
| QR Code | `events:qrcode` | `GET /events/{id}/qrcode` |
| Participar | `events:participation_create` | `POST /events/{id}/participations` |
| Recusar | `events:participation_decline` | `POST /events/{id}/participations/decline` |
| Cancelar | `events:participation_cancel` | `POST /events/{id}/participations/cancel` |
| Fornecedores (lista) | `suppliers:list` | `GET /suppliers` |
| Fornecedor (criar) | `suppliers:create` | `POST /suppliers` |
| Fornecedor (detalhe) | `suppliers:detail` | `GET /suppliers/{id}` |
| Fornecedor (editar) | `suppliers:update` | `PATCH /suppliers/{id}` |
| Dashboard | `dashboard:index` | `GET /dashboard` |
