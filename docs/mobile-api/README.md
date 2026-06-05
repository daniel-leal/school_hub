# Documentação — School Hub Mobile (API + Flutter)

Esta pasta reúne **toda a documentação necessária** para reimplementar o School Hub
como aplicativo mobile em **Flutter**, consumindo uma **API REST** que expõe as
funcionalidades, regras de negócio e fluxos existentes hoje na aplicação web Django.

> O backend atual é um monólito Django 5.1 com renderização server-side (templates).
> Esta documentação descreve **o que o sistema faz hoje** e **como expor isso como API**
> para que um cliente Flutter consuma. Os contratos de API aqui descritos ainda **não
> existem no código** — são a especificação-alvo a ser implementada (camada DRF).

## Como ler esta documentação

| # | Documento | Para quê |
|---|-----------|----------|
| 00 | [README.md](./README.md) | Este índice |
| 01 | [01-visao-geral.md](./01-visao-geral.md) | Produto, problema/solução, personas, glossário |
| 02 | [02-arquitetura.md](./02-arquitetura.md) | Arquitetura atual + arquitetura-alvo da API mobile |
| 03 | [03-modelo-de-dominio.md](./03-modelo-de-dominio.md) | Entidades, campos, relacionamentos, diagrama ER |
| 04 | [04-regras-de-negocio.md](./04-regras-de-negocio.md) | Todas as regras de negócio por domínio |
| 05 | [05-autenticacao-permissoes.md](./05-autenticacao-permissoes.md) | Autenticação (JWT) e matriz de permissões |
| 06 | [06-referencia-api.md](./06-referencia-api.md) | Referência completa de endpoints REST |
| 07 | [07-pix.md](./07-pix.md) | Geração de PIX (EMV / BR Code) e QR Code |
| 08 | [08-notificacoes.md](./08-notificacoes.md) | E-mails transacionais e push (futuro) |
| 09 | [09-fluxos-mobile.md](./09-fluxos-mobile.md) | Fluxos de tela e sequências para o app |
| — | [openapi.yaml](./openapi.yaml) | Contrato OpenAPI 3.1 (para codegen no Flutter) |

## Resumo do produto em uma frase

Plataforma para **pais/responsáveis** organizarem **eventos escolares de uma turma**
— arrecadações com PIX, lanches partilhados e confirmações de presença — substituindo
a bagunça dos grupos de WhatsApp.

## Domínios (apps Django)

| Domínio | Responsabilidade |
|---------|------------------|
| `core` | Modelos base (UUID, timestamps, soft-delete), serviço PIX, serviço de e-mail, DI |
| `accounts` | `User` (login por e-mail) + perfil `Guardian` (responsável) |
| `classes` | `SchoolClass`, `ClassMember`, `Student`, convites (`ClassInvitation`) |
| `events` | `Event`, `EventItem`, `Payment`, `EventParticipation` |
| `suppliers` | `Supplier` (fornecedores/contatos úteis) |
| `dashboard` | Estatísticas agregadas do responsável |

## Convenções da API-alvo

- **Base URL:** `/api/v1`
- **Formato:** JSON (`application/json`); upload de comprovante em `multipart/form-data`
- **IDs:** UUID v4 (string) para todas as entidades de negócio
- **Datas:** ISO-8601 (`event_date` é `YYYY-MM-DD`; timestamps são `date-time` UTC)
- **Dinheiro:** string decimal com 2 casas (ex.: `"150.00"`), em BRL
- **Idioma:** rótulos/UI em **pt-BR**; chaves JSON em **inglês** (espelham os modelos)
- **Autenticação:** Bearer JWT (ver doc 05)
- **Paginação:** `?page=N` (12 itens por página, como hoje); resposta com `count/next/previous/results`

## Status atual vs. alvo

- ✅ **Existe hoje:** modelos, regras de negócio, serviço PIX, serviço de e-mail,
  views server-side, admin (Django Unfold), armazenamento S3 (MinIO/R2) para comprovantes.
- 🎯 **A construir para o mobile:** camada REST (DRF), autenticação por token (JWT),
  serializers, OpenAPI, e possivelmente push notifications.
- 🔌 **Único endpoint JSON existente hoje:** `GET /accounts/api/pix-info/`
  (retorna a chave PIX do responsável logado).
