# 08 — Notificações

## 8.1 E-mails transacionais (existem hoje)

Implementados em `EmailService` (`apps/core/services/email.py`). São disparados de forma
**resiliente** (falha de envio é apenas logada, nunca quebra o fluxo). Templates em
`templates/emails/` (versão `.html` + `.txt`).

| Evento de negócio | Quando dispara | Destinatário | Template | Disparado por |
|-------------------|----------------|--------------|----------|---------------|
| **Convite para turma** | Ao criar convite **com e-mail** | e-mail do convidado | `invitation` | `CreateInvitationView` → `send_invitation_email` |
| **Novo evento** | Ao criar um evento | **todos os membros** da turma | `event_notification` | `EventCreateView` → `send_event_notification_email` (`send_mass_mail`) |
| **Status de pagamento** | Ao **confirmar** ou **rejeitar** pagamento | responsável pagador | `payment_status` | `PaymentConfirmView`/`PaymentRejectView` → `send_payment_status_email` |

Detalhes:
- **Convite:** só envia se `invitation.email` estiver preenchido (convite genérico não
  envia e-mail). O corpo contém o `invite_url` (link com token).
- **Novo evento:** envia para `guardian.user.email` de cada membro com e-mail; usa
  `send_mass_mail` (uma mensagem por destinatário). Assunto: "Novo evento: {título}".
- **Pagamento:** assunto "Atualização do pagamento — {título do evento}".

Configuração SMTP via `EMAIL_*` (dev usa MailHog em `localhost:1025`; backend de console
como fallback). `DEFAULT_FROM_EMAIL` define o remetente.

## 8.2 Impacto na API mobile

Os e-mails continuam sendo enviados pelo backend **quando os respectivos endpoints da
API forem chamados** (criar convite, criar evento, confirmar/rejeitar pagamento). O app
não precisa fazer nada além de chamar os endpoints — o efeito colateral de e-mail é do
servidor.

## 8.3 Push notifications (não existe hoje — recomendação)

Para um app mobile, e-mail não basta. Recomenda-se adicionar **push** (FCM/APNs) para
os mesmos gatilhos de negócio, além de novos:

| Gatilho | Push sugerido | Para quem |
|---------|---------------|-----------|
| Novo evento na turma | "Novo evento: {título}" | membros da turma |
| Pagamento confirmado/rejeitado | "Seu pagamento foi {status}" | pagador |
| Novo pagamento pendente | "Novo comprovante para confirmar" | quem pode confirmar (admin/criador/responsável) |
| Convite aceito | "{nome} entrou na turma" | admin que convidou |
| Lembrete de evento próximo | "Festa Junina é amanhã" | membros com participação pendente |
| Participação pendente | "Confirme presença em {evento}" | membros sem participação |

### Como implementar (sugestão de contrato)
- `POST /me/devices` — registra o device token do app
  `{ "platform": "android|ios", "token": "fcm-token", "app_version": "1.0.0" }`
- `DELETE /me/devices/{token}` — remove no logout.
- Backend: tabela `Device(guardian, platform, token)`; serviço de push (ex.: `firebase-admin`
  ou pacote Django de FCM) chamado nos mesmos pontos que hoje disparam e-mail.
- Respeitar preferências (futuro): `GET/PATCH /me/notification-preferences`.

> Esta seção é **roadmap**; o backend atual não tem push. Inclua na fase 2 do mobile.
