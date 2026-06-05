# 07 — PIX (EMV / BR Code) e QR Code

A geração de PIX é feita pelo serviço `PixService` (`apps/core/services/pix.py`),
seguindo o padrão **EMV BR Code** do Banco Central. O app **não precisa** reimplementar
isso — apenas consumir os endpoints. Este documento explica o comportamento para que a
API e o app o exponham corretamente.

## 7.1 O que o serviço gera

- **Código "copia e cola" (BR Code):** string EMV pronta para colar em qualquer app de
  banco (`pix_code`).
- **QR Code:** imagem PNG do mesmo BR Code.

Configuração por evento (em `EventPixView`/`EventQRCodeView`):
- `pix_key` = `event.pix_key`
- `merchant_name` = `event.pix_holder_name` ou `"SCHOOL HUB"`
- `merchant_city` = `"SAO PAULO"` (fixo no código atual)
- `amount` = `event.individual_amount` (ou `0.00`)
- `transaction_id (txid)` = `event.id.hex[:25]` (UUID sem hífens, 25 chars)
- `description` = `event.title[:25]`

> Há também `PixService` registrado no container de DI com `PIX_KEY`/`PIX_MERCHANT_NAME`/
> `PIX_MERCHANT_CITY` globais (settings), mas o fluxo de evento usa a chave do **evento**.

## 7.2 Estrutura EMV (campos do BR Code)

| Tag | Campo | Valor |
|-----|-------|-------|
| 00 | Payload Format Indicator | `01` |
| 26 | Merchant Account Info (PIX) | GUI `br.gov.bcb.pix` + chave normalizada + descrição opcional |
| 52 | Merchant Category Code | `0000` |
| 53 | Transaction Currency | `986` (BRL) |
| 54 | Transaction Amount | valor, se `> 0` |
| 58 | Country Code | `BR` |
| 59 | Merchant Name | nome normalizado (máx 25) |
| 60 | Merchant City | cidade normalizada (máx 15) |
| 62 | Additional Data Field | txid (tag 05) |
| 63 | CRC16 | checksum CRC16-CCITT-FALSE (poly `0x1021`, init `0xFFFF`) |

Observações de compatibilidade já tratadas no serviço:
- O campo **01 (Point of Initiation)** é **omitido** de propósito, para máxima
  compatibilidade com apps de banco em códigos gerados manualmente.
- `merchant_name`/`merchant_city`/`description`/`txid` são **normalizados**: remoção de
  acentos, apenas alfanumérico (e espaço, exceto txid), maiúsculas e truncamento.

## 7.3 Normalização da chave PIX

O serviço detecta e normaliza o tipo de chave (`_normalize_pix_key`):
- **E-mail:** mantém em minúsculas.
- **Chave aleatória (EVP/UUID):** formata como UUID com hífens, minúsculas.
- **CPF:** se vier formatado `000.000.000-00` → só dígitos (11).
- **CNPJ:** `00.000.000/0000-00` → só dígitos (14).
- **Telefone:** normaliza para E.164 (`+55DDDNUMERO`); detecta DDD, 9º dígito, etc.
- Fallback: retorna como veio.

> Consequência prática para o app: **o usuário pode digitar a chave PIX em qualquer
> formato comum** (e-mail, telefone com parênteses, CPF pontuado, chave aleatória) que o
> backend normaliza. O app só precisa enviar o texto digitado.

## 7.4 Como o app consome

1. Abrir a tela de pagamento de um evento de arrecadação.
2. `GET /events/{id}/pix` → recebe `pix_code` (copia e cola) + `qr_code_base64`.
   - Mostrar o QR (decodificar base64 → `Image.memory` no Flutter).
   - Botão "copiar código" com `pix_code`.
   - Botão "compartilhar no WhatsApp" com o `pix_code` (o caso de uso original do produto).
3. O usuário paga no app do banco e volta para **enviar o comprovante**
   (`POST /events/{id}/payments`, multipart).
4. Um responsável/admin **confirma** o pagamento (`POST /payments/{id}/confirm`).

Alternativa para exibir o QR: `GET /events/{id}/qrcode` retorna PNG direto
(`Image.network` com header `Authorization`).

## 7.5 Erros

- Evento sem `pix_key` → a API retorna `400`/`404` ("PIX não configurado").
  O app deve esconder a aba de PIX nesse caso (checar `event.pix_key`/`has_pix`).
