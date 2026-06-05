# 09 — Fluxos Mobile (telas e sequências)

Sugestão de fluxos de tela para o app Flutter, mapeados aos endpoints do doc 06.
Não prescreve UI; foca na sequência de chamadas e regras.

## 9.1 Onboarding e autenticação

```
[Splash] → tem token válido?
   ├─ sim → [Dashboard]
   └─ não → [Login]
              ├─ "Criar conta" → [Cadastro] (opcional: deep link com class_code)
              └─ login OK → guarda access+refresh → [Dashboard]
```
- Cadastro: `POST /auth/register` (pode trazer `class_code` de um deep link de convite).
- Login: `POST /auth/login`. Guardar tokens no `flutter_secure_storage`.
- Interceptor HTTP: em `401`, tentar `POST /auth/refresh`; se falhar → logout.

## 9.2 Entrar em uma turma

Dois caminhos:
1. **Código:** tela "Entrar em turma" → `POST /classes/join { invite_code }`.
2. **Link de convite (deep link):** abre `GET /invitations/{token}` (mostra a turma) →
   `POST /invitations/{token}/accept`.

```
[Minhas turmas] (vazio)
   → [Entrar / Criar]
        ├─ Criar → POST /classes → vira admin → [Detalhe da turma]
        └─ Entrar (código) → POST /classes/join → [Detalhe da turma]
```

## 9.3 Cadastrar aluno

Pré-requisito para pagar/participar (RN-PG-01, RN-PT-02).
```
[Detalhe da turma] → "Adicionar aluno"
   → POST /classes/{id}/students { name, birth_date?, notes? }
   → aluno aparece em "meus alunos"
```

## 9.4 Criar evento (admin/membro)

```
[Detalhe da turma] → "Novo evento"
   → escolhe tipo: Arrecadação | Lanche Partilhado | Presença
   → POST /classes/{id}/events {...}
       (se Arrecadação e budget informado → individual_amount calculado)
   → backend envia e-mail aos membros
   → [Detalhe do evento]
```

A tela de criação deve adaptar campos por tipo:
- **Arrecadação:** mostra `budget`, `pix_key`, `pix_holder_name`, `individual_amount`.
- **Lanche Partilhado / Presença:** esconde campos financeiros; foco em itens/participação.

## 9.5 Pagar um evento de arrecadação

```
[Detalhe do evento (payment)]
   ├─ aba "PIX": GET /events/{id}/pix → mostra QR + "copia e cola" + compartilhar
   ├─ usuário paga no app do banco
   └─ "Enviar comprovante":
        valor pré-preenchido = individual_amount × nº de alunos do responsável
        POST /events/{id}/payments (multipart: amount, receipt, notes)
          ├─ 201 → "Aguardando confirmação"
          ├─ 409 → "Você já enviou um pagamento"
          └─ 403 → "Cadastre um aluno nesta turma primeiro"
```
Lado de quem confirma (admin/criador/responsável):
```
[Detalhe do evento] → lista "Pagamentos pendentes"
   → ver comprovante (receipt_url)
   → Confirmar: POST /payments/{id}/confirm  (envia e-mail ao pagador)
   → Rejeitar:  POST /payments/{id}/reject   (envia e-mail ao pagador)
```

## 9.6 Lanche partilhado (potluck)

```
[Detalhe do evento (potluck)]
   → "Vou levar": POST /events/{id}/participations { contribution } (obrigatório)
   → aparece na lista "Confirmados — o que cada um leva"
   → pode cancelar: POST /events/{id}/participations/cancel
   → ou recusar:    POST /events/{id}/participations/decline { notes? }
```
Itens do evento (lista do que falta levar) podem ser geridos por:
```
   → "Adicionar item" (can_edit): POST /events/{id}/items
   → "Assumir item": POST /items/{id}/assign
   → "Concluir": POST /items/{id}/complete
```

## 9.7 Confirmação de presença (presence)

```
[Detalhe do evento (presence)]
   → "Confirmar presença": POST /events/{id}/participations { guests_count }
   → "Não vou": POST /events/{id}/participations/decline { notes? }
   → cancelar confirmação: POST /events/{id}/participations/cancel
```

## 9.8 Dashboard (home)

```
[Dashboard] = GET /dashboard
   ├─ cards: turmas, alunos, eventos ativos, pagamentos pendentes
   ├─ gráfico de despesas mensais (monthly_expenses)
   ├─ próximos eventos (upcoming_events) → toca → [Detalhe do evento]
   ├─ aniversariantes do mês (birthdays)
   └─ minhas turmas (classes) → toca → [Detalhe da turma]
```

## 9.9 Fornecedores

```
[Fornecedores] = GET /suppliers (?q=&category=)
   ├─ filtro por categoria: GET /suppliers/categories
   └─ [Detalhe do fornecedor] = GET /suppliers/{id}
        → botões: WhatsApp (whatsapp_link), Instagram (instagram_link), Maps (maps_link)
        → ligar (phone), e-mail, site
   → "Adicionar fornecedor": POST /suppliers
```

## 9.10 Sequência — pagamento de ponta a ponta (diagrama)

```
Pagador          App            API                Responsável/Admin
  │   abre evento  │             │                        │
  │ ──────────────►│ GET /events/{id}                     │
  │                │────────────►│                        │
  │   vê PIX       │ GET /events/{id}/pix                 │
  │ ◄──────────────│◄────────────│                        │
  │ paga no banco  │             │                        │
  │   envia compr. │ POST /events/{id}/payments (multipart)
  │ ──────────────►│────────────►│ status=pending         │
  │   "pendente"   │◄────────────│                        │
  │                │             │   push/e-mail ─────────►│ "novo comprovante"
  │                │             │   POST /payments/{id}/confirm
  │                │             │◄───────────────────────│
  │                │             │ status=confirmed       │
  │   e-mail ◄─────────────────  │ send_payment_status    │
  │   (app atualiza ao reabrir o evento: has_paid=true)   │
```

## 9.11 Estados e telas vazias (checklist para o app)

- Sem turmas → CTA "Criar ou entrar em turma".
- Turma sem alunos → bloqueio amigável antes de pagar/participar (RN-PG-01/RN-PT-02).
- Evento sem `pix_key` → esconder aba PIX.
- Evento encerrado (`is_active=false`) → modo somente leitura.
- Pagamento `rejected` → permitir reenviar? (hoje a regra é 1 por evento — avaliar
  com o produto se rejeição libera novo envio; **o código atual não libera**).
- Sem conexão → cache local dos GETs principais (dashboard, turmas, eventos).
