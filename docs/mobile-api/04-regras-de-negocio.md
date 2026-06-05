# 04 — Regras de Negócio

Todas as regras abaixo foram extraídas do código atual (models, views, forms, services).
Elas **devem ser preservadas** na camada de API. A maioria já está implementada nos
modelos — a API deve reutilizá-las.

## 4.1 Conta e responsável

- **RN-AC-01** — Login é por **e-mail + senha**; e-mail é único no sistema.
- **RN-AC-02** — Senha segue os validadores do Django: similaridade com atributos do
  usuário, comprimento mínimo, senha comum e senha totalmente numérica.
- **RN-AC-03** — Ao registrar um usuário, **cria-se automaticamente um `Guardian`**
  vinculado. Em vários fluxos, se o `Guardian` não existir, ele é criado sob demanda.
- **RN-AC-04** — No registro pode ser informado um `class_code` (código de convite da
  turma). Se válido (turma existente e ativa), o novo responsável é **adicionado à
  turma como `member`** automaticamente.
- **RN-AC-05** — O perfil é editável em duas partes: dados do `User`
  (`first_name`, `last_name`, `phone`) e dados do `Guardian`
  (`cpf`, `pix_key`, `pix_holder_name`, `address`, `notes`).
- **RN-AC-06** — Informação de PIX do responsável: `pix_key` (pode estar vazia) e
  `pix_holder_name` (se vazio, usa o nome completo do usuário como padrão).

## 4.2 Turmas

- **RN-CL-01** — Ao criar uma turma, o `invite_code` é **gerado automaticamente**: 10
  caracteres maiúsculos (derivado de `secrets.token_urlsafe(8)`), garantidamente único.
- **RN-CL-02** — O **criador da turma** vira `ClassMember` com papel `admin`
  (em transação atômica junto à criação da turma).
- **RN-CL-03** — A listagem de turmas mostra **apenas turmas ativas das quais o
  responsável é membro**.
- **RN-CL-04** — `year` (ano letivo) tem como padrão o **ano corrente**.
- **RN-CL-05** — `member_count`, `student_count` e `active_events_count` são derivados
  e devem ser expostos na API (para cards/listas).
- **RN-CL-06** — Entrar em turma por código:
  - Se o código for inválido → erro.
  - Se válido e o responsável **ainda não é membro** → cria vínculo `member`.
  - Se já é membro → não duplica (informa que já participa).
- **RN-CL-07** — A turma pode ser editada (campos `name`, `school`, `year`,
  `description`). Recomenda-se restringir edição a **admins da turma** na API
  (a web atual não restringe explicitamente — ver nota de segurança no doc 05).
- **RN-CL-08** — `regenerate_invite_code()` existe no modelo (gera novo código). Hoje
  **não há rota web** para isso; recomenda-se expor como endpoint **somente admin**.

## 4.3 Alunos

- **RN-ST-01** — Um aluno pertence a **uma turma** e é "dono" de **um responsável**
  (`guardian`). Ao criar, `guardian` = responsável logado e `school_class` = turma da rota.
- **RN-ST-02** — Editar/excluir aluno é permitido **apenas para o responsável dono**
  do aluno (queryset filtra por `guardian=request.user.guardian`).
- **RN-ST-03** — `birth_date` é opcional, mas alimenta o recurso de **aniversariantes
  do mês** no dashboard.
- **RN-ST-04** — `notes` guarda informações sensíveis (alergias, restrições).

## 4.4 Convites

- **RN-IN-01** — `token` é gerado automaticamente (`secrets.token_urlsafe(32)`), único.
- **RN-IN-02** — `expires_at` padrão = criação **+ 7 dias** (se não informado).
- **RN-IN-03** — Convite é **válido** apenas se `status == pending` **e** não expirado.
- **RN-IN-04** — `email` vazio = **convite genérico** (qualquer um com o link entra).
  Com e-mail = convite direcionado, e o sistema **envia e-mail** com o link.
- **RN-IN-05** — Aceitar convite:
  - Se inválido → erro ("Este convite não é mais válido.").
  - Se válido → cria/garante `ClassMember` (role `member`), e marca o convite como
    `accepted` com `accepted_at` e `accepted_by`.
- **RN-IN-06** — `invited_by` = responsável que criou o convite.

## 4.5 Eventos

- **RN-EV-01** — Há **3 tipos** de evento: `payment` (arrecadação), `potluck`
  (lanche partilhado), `presence` (confirmação de presença). O tipo `mixed` foi removido.
- **RN-EV-02** — Ao criar um evento:
  - `created_by` = responsável logado.
  - `responsible` (responsável pela arrecadação) = **o mesmo criador**, por padrão.
  - Se `budget` informado e `individual_amount` vazio → `individual_amount` é
    **calculado automaticamente** = `budget / nº de alunos da turma` (2 casas decimais).
  - Após criar, é **enviado e-mail de notificação** a todos os membros da turma.
- **RN-EV-03** — Ao editar, se `budget` mudou e `individual_amount` continua vazio,
  recalcula `individual_amount`.
- **RN-EV-04** — `requires_participation` é `true` para `potluck` e `presence`;
  `false` para `payment`. Define se o evento aceita confirmação de participação.
- **RN-EV-05** — A listagem de eventos mostra **eventos ativos das turmas do
  responsável**.
- **RN-EV-06** — Encerrar evento: `is_active=false` e `closed_at=now`. Não há "reabrir"
  no código atual.
- **RN-EV-07** — Progresso financeiro:
  - `total_collected` = soma de pagamentos **confirmados**.
  - `total_pending` = `budget - total_collected` (0 se sem budget).
  - `payment_progress_percentage` = `min(100, round(total_collected/budget*100))`.

## 4.6 Itens do evento

- **RN-IT-01** — Tipos: `expense` (despesa) e `contribution` (contribuição, padrão).
- **RN-IT-02** — `total_price` = `unit_price * quantity` (nulo se sem preço).
- **RN-IT-03** — "Assumir item": define `assigned_to` = responsável logado.
- **RN-IT-04** — "Concluir item": `is_completed = true`.
- **RN-IT-05** — Quantidade mínima 1.

## 4.7 Pagamentos

- **RN-PG-01** — Para **enviar um pagamento**, o responsável precisa ter **pelo menos
  um aluno vinculado àquela turma**. Caso contrário, é bloqueado.
- **RN-PG-02** — **Um pagamento por responsável por evento.** Se já existe pagamento
  desse responsável no evento, não permite criar outro (avisa que já enviou).
- **RN-PG-03** — Valor sugerido (pré-preenchido) = `individual_amount × nº de alunos
  do responsável na turma` (mínimo 1 aluno). Se não houver `individual_amount`, o valor
  fica em aberto.
- **RN-PG-04** — Comprovante (`receipt`): opcional no modelo, mas é o fluxo principal.
  Validação: extensões `jpg, jpeg, png, gif, webp, pdf`; tamanho **máx. 10 MB**.
- **RN-PG-05** — Pagamento nasce com `status = pending`.
- **RN-PG-06** — **Confirmar** pagamento → `status = confirmed`, grava `confirmed_by`
  e `confirmed_at`, e **envia e-mail** ao pagador informando o novo status.
- **RN-PG-07** — **Rejeitar** pagamento → `status = rejected` e **envia e-mail** ao
  pagador.
- **RN-PG-08** — Quem pode confirmar/rejeitar: **admin da turma**, **criador do evento**
  ou **responsável pela arrecadação** (`event.responsible`). Sem permissão → erro.
- **RN-PG-09** — Todos os membros podem **ver** quem pagou e quem está pendente
  (`paid_students`, `pending_students`).

## 4.8 PIX

- **RN-PX-01** — O código PIX do evento é gerado a partir de `event.pix_key`,
  `event.pix_holder_name` (ou "SCHOOL HUB"), cidade "SAO PAULO", valor
  `individual_amount` e `txid` derivado do UUID do evento (`id.hex[:25]`).
- **RN-PX-02** — Se o evento **não** tem `pix_key`, não há PIX/QR (a API deve retornar
  404/400 indicando "PIX não configurado").
- **RN-PX-03** — A geração segue o padrão **EMV BR Code** do Banco Central, com cálculo
  de CRC16 e normalização da chave (e-mail/telefone/CPF/CNPJ/aleatória).
  Detalhes em [07-pix.md](./07-pix.md).
- **RN-PX-04** — O QR Code é uma imagem **PNG**; a API pode retorná-la como binário
  (`image/png`) e/ou como **base64** dentro de um JSON, junto do "copia e cola".

## 4.9 Participações (lanche partilhado / presença)

- **RN-PT-01** — Só é possível confirmar participação em eventos que
  `requires_participation` (`potluck` ou `presence`). Em `payment` → erro.
- **RN-PT-02** — O responsável precisa ter **pelo menos um aluno na turma** do evento.
- **RN-PT-03** — **Uma participação por responsável por evento** (restrição única). O
  fluxo usa `get_or_create` e depois `confirm`/`decline`.
- **RN-PT-04** — Em `potluck`, o campo `contribution` (o que vai levar) é **obrigatório**.
- **RN-PT-05** — Em `presence`, usa-se `guests_count` (quantas pessoas; default 1,
  faixa sugerida 1–20). Em outros tipos, `guests_count` é forçado a 1.
- **RN-PT-06** — **Confirmar** → `status=confirmed`, grava `confirmed_at` e os dados
  (`contribution`, `guests_count`, `notes`).
- **RN-PT-07** — **Recusar** → `status=declined` (aceita `notes` com o motivo).
- **RN-PT-08** — **Cancelar** participação confirmada → na prática faz `decline` com
  nota "Cancelado pelo usuário". Só funciona se a participação estava `confirmed`.
- **RN-PT-09** — Se já confirmou, tentar confirmar de novo apenas informa que já
  confirmou (idempotente do ponto de vista do usuário).

## 4.10 Fornecedores

- **RN-SP-01** — Listagem mostra apenas fornecedores **ativos** (`is_active=true`),
  ordenados por **recomendados primeiro** (`is_recommended`) e depois por nome.
- **RN-SP-02** — Busca por `q` (nome contém) e filtro por `category` (contém).
- **RN-SP-03** — As categorias disponíveis vêm dos valores **distintos** de
  `Supplier.category` (entre fornecedores ativos, ignorando vazios).
- **RN-SP-04** — Links derivados expostos na API:
  - `whatsapp_link` = `https://wa.me/55<somente dígitos de whatsapp ou phone>`
  - `instagram_link` = `https://instagram.com/<instagram sem @>`
  - `maps_link` = `maps_url` (se houver) ou busca Google Maps pelo `address`
- **RN-SP-05** — `rating` é de 1 a 5 (opcional). `is_recommended` destaca o fornecedor.
- **RN-SP-06** — Fornecedores são **globais** (não pertencem a uma turma) e visíveis a
  qualquer responsável autenticado.

## 4.11 Dashboard

Para o responsável logado, agrega (apenas suas turmas/alunos/pagamentos):
- **RN-DB-01** — `total_classes` = turmas ativas das quais é membro.
- **RN-DB-02** — `total_students` = alunos do responsável.
- **RN-DB-03** — `total_events` = todos os eventos das suas turmas;
  `active_events` = eventos ativos com `event_date >= hoje`.
- **RN-DB-04** — `upcoming_events` = próximos 5 eventos ativos (data ≥ hoje), ordenados
  por data.
- **RN-DB-05** — `total_payments` = soma de **todos** os pagamentos do responsável
  (qualquer status); `pending_payments_count` = pagamentos pendentes.
- **RN-DB-06** — Gráfico mensal: soma de pagamentos **confirmados** por mês (até 12
  meses), com labels `"mon/yy"`.
- **RN-DB-07** — `recent_payments` = últimos 5 pagamentos do responsável.
- **RN-DB-08** — `classes` com contadores de eventos e alunos (distintos).
- **RN-DB-09** — `birthdays` = alunos das turmas do responsável que **aniversariam no
  mês corrente**, ordenados pelo dia.

## 4.12 Regras transversais

- **RN-GL-01** — Todas as entidades de negócio usam **UUID** como id (exceto `User`,
  que usa inteiro).
- **RN-GL-02** — `created_at`/`updated_at` automáticos em todas as entidades.
- **RN-GL-03** — Soft-delete disponível em entidades que herdam `SoftDeleteModel`
  (registros excluídos ficam ocultos por padrão; há `restore()` e `hard_delete()`).
- **RN-GL-04** — Paginação padrão de **12 itens** por página em listagens
  (turmas, eventos, fornecedores).
- **RN-GL-05** — Idioma da UI: **pt-BR**; timezone `America/Sao_Paulo`; moeda BRL.
