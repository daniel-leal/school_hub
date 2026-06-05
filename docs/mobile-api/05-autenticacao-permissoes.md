# 05 — Autenticação e Permissões

## 5.1 Autenticação (alvo: JWT)

A web atual usa **sessão + cookie** (`LoginView`/`LogoutView` do Django,
`LoginRequiredMixin` em todas as views protegidas). Para o app Flutter, recomenda-se
**JWT** (`djangorestframework-simplejwt`).

### Fluxo de tokens

```
App Flutter                         API (/api/v1)
   │                                     │
   │  POST /auth/register {email,...}    │
   │ ───────────────────────────────────►│  cria User + Guardian
   │  201 {user, access, refresh}        │  (opcional: já entra na turma via class_code)
   │ ◄───────────────────────────────────│
   │                                     │
   │  POST /auth/login {email,password}  │
   │ ───────────────────────────────────►│
   │  200 {access, refresh}              │
   │ ◄───────────────────────────────────│
   │                                     │
   │  GET /events  (Bearer access)       │
   │ ───────────────────────────────────►│
   │  200 [...]                          │
   │ ◄───────────────────────────────────│
   │                                     │
   │  (access expirou) 401               │
   │  POST /auth/refresh {refresh}       │
   │ ───────────────────────────────────►│
   │  200 {access}                       │
   │ ◄───────────────────────────────────│
```

### Recomendações
- `access` curto (ex.: 15–60 min), `refresh` longo (ex.: 7–30 dias).
- Armazenar tokens com `flutter_secure_storage` (Keychain/Keystore).
- Enviar sempre `Authorization: Bearer <access>` nos endpoints protegidos.
- `POST /auth/logout` faz blacklist do `refresh` (com a app de blacklist do SimpleJWT).
- Aplicar **throttling** em `/auth/login` e `/auth/register` (anti brute-force).

### Endpoints de autenticação (resumo — detalhes no doc 06)
| Método | Rota | Protegido | Descrição |
|--------|------|-----------|-----------|
| POST | `/auth/register` | não | Cria usuário + responsável |
| POST | `/auth/login` | não | Retorna `access` + `refresh` |
| POST | `/auth/refresh` | não (usa refresh) | Renova `access` |
| POST | `/auth/logout` | sim | Invalida o `refresh` |
| POST | `/auth/password/change` | sim | Altera a senha |
| GET/PATCH | `/me` | sim | Perfil (User + Guardian) |
| GET | `/me/pix` | sim | Info de PIX do responsável |

## 5.2 Identidade no app

- Todo endpoint protegido resolve o `Guardian` a partir do usuário autenticado
  (`request.user.guardian`). Se não existir, **cria sob demanda** (como hoje).
- O app nunca manipula `User.id`/`Guardian.id` de terceiros diretamente; sempre opera
  no contexto do responsável logado e de turmas/eventos a que ele pertence.

## 5.3 Modelo de permissões (contextual)

Não existem papéis globais para o usuário comum. As permissões são **por turma** e
**por evento**:

### Papéis por turma
| Papel | Como se obtém | Pode |
|-------|---------------|------|
| **Membro** (`member`) | Entrou por código/convite | Ver turma, ver eventos, cadastrar próprios alunos, pagar, participar |
| **Admin** (`admin`) | Criou a turma (ou foi promovido) | Tudo do membro + editar turma, criar convites, confirmar/rejeitar pagamentos de qualquer evento da turma |

### Papéis por evento (derivados no `EventDetailView`)
- `is_admin` — é admin da turma do evento.
- `is_creator` — `event.created_by == guardian`.
- `is_responsible` — `event.responsible == guardian`.
- `can_edit` = `is_admin OR is_creator`.
- `can_confirm_payments` = `is_admin OR is_creator OR is_responsible`.

## 5.4 Matriz de permissões (ação → quem pode)

| Ação | Membro | Admin turma | Criador evento | Responsável arrecadação | Regra extra |
|------|:------:|:-----------:|:--------------:|:-----------------------:|-------------|
| Ver turma / eventos / fornecedores | ✅ | ✅ | ✅ | ✅ | precisa ser membro da turma |
| Criar turma | ✅ (vira admin) | — | — | — | — |
| Editar turma | ❌¹ | ✅ | — | — | ¹recomendado restringir |
| Criar convite | ❌¹ | ✅ | — | — | ¹recomendado restringir |
| Aceitar convite | ✅ | ✅ | — | — | convite válido |
| Cadastrar aluno | ✅ | ✅ | — | — | aluno fica do próprio responsável |
| Editar/excluir aluno | apenas dono | apenas dono | — | — | `guardian == request.guardian` |
| Criar evento | ✅ | ✅ | — | — | vira criador+responsável |
| Editar evento | ❌ | ✅ | ✅ | ❌ | `can_edit` |
| Encerrar evento | ❌¹ | ✅ | ✅ | — | ¹recomendado restringir |
| Adicionar/editar item | ✅¹ | ✅ | ✅ | — | ¹web atual não restringe |
| Assumir/concluir item | ✅ | ✅ | ✅ | ✅ | qualquer membro |
| Enviar pagamento | ✅ | ✅ | ✅ | ✅ | precisa ter aluno na turma; 1 por evento |
| Confirmar/rejeitar pagamento | ❌ | ✅ | ✅ | ✅ | `can_confirm_payments` |
| Confirmar/recusar/cancelar participação | ✅ | ✅ | ✅ | ✅ | evento `potluck`/`presence`; precisa ter aluno na turma |
| Ver PIX/QR do evento | ✅ | ✅ | ✅ | ✅ | evento precisa ter `pix_key` |
| CRUD fornecedor | ✅ | ✅ | — | — | global; qualquer autenticado |

## 5.5 Notas de segurança para a implementação da API

A camada web atual protege com `LoginRequiredMixin`, mas em alguns pontos **não checa
explicitamente a pertença/papel** (confia na navegação por links). Ao expor como API
pública, a camada DRF **deve** adicionar permissões explícitas. Pontos de atenção:

1. **Pertença à turma:** todo acesso a turma/evento/itens/pagamentos/participações deve
   validar que o `request.guardian` é **membro da turma** do recurso. Hoje, p.ex.,
   `EventDetailView` não bloqueia quem não é membro — a API **deve** bloquear (403/404).
2. **Edição de turma/evento:** `ClassUpdateView`/`EventUpdateView` não checam papel hoje;
   a API deve exigir `is_admin` (turma) ou `can_edit` (evento).
3. **Itens e encerramento:** `EventItemCreate/Update`, `EventClose` não checam papel hoje;
   recomenda-se exigir `can_edit` para criar/editar item e encerrar evento.
4. **Confirmar/rejeitar pagamento:** já checa `can_confirm_payments` — manter.
5. **Alunos:** já restringe ao dono via queryset — manter (retornar 404 para alunos de
   terceiros, não 403, para não vazar existência).
6. **IDOR:** como os IDs são UUID (não sequenciais), o risco de enumeração é menor, mas
   ainda assim **autorize por pertença**, nunca confie só no UUID.
7. **Upload de comprovante:** validar extensão e tamanho (≤10 MB) no serializer; o
   storage é privado — gerar URLs assinadas se o bucket não for público.
8. **Rate limiting:** login, registro e refresh.

> Resumo: trate a web atual como referência **funcional**, mas implemente autorização
> **explícita e por pertença** na API — não replique as lacunas implícitas da web.
