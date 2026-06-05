# 01 — Visão Geral do Produto

## Problema

Eventos escolares são organizados por pais/responsáveis em grupos de WhatsApp, sem
organização adequada. Isso dificulta o controle de pagamentos e de eventos paralelos.

Exemplo real: em uma mesma semana há um evento de Dia das Mães que exige a compra de
itens de papelaria e roupas dos alunos, enquanto, ao mesmo tempo, os pais decidem
comprar um presente para as professoras que também são mães. Isso gera múltiplas
transferências bancárias, com pais diferentes responsáveis por cada item. A cada
comprovante enviado, é preciso marcar manualmente quem já transferiu e quem não.

## Solução

O **School Hub** centraliza a gestão de eventos escolares em uma única plataforma:

- **Gestão de turmas:** criação de turmas e convites para outros pais entrarem.
- **Eventos flexíveis:** arrecadações financeiras, lanches partilhados e confirmação
  de presença.
- **Integração PIX:** geração automática de QR Code e código "copia e cola" (BR Code).
- **Gestão de pagamentos:** upload de comprovante e confirmação do pagamento.
- **Dashboard:** visão geral de eventos ativos, totais e despesas ao longo do ano.
- **Fornecedores:** cadastro de contatos úteis (costureiras, decoradores, buffets)
  com integração opcional ao Google Maps / WhatsApp / Instagram.

## Personas

| Persona | Descrição | No sistema |
|---------|-----------|-----------|
| **Responsável (Guardian)** | Pai/mãe/responsável por um ou mais alunos. Usuário final do app. | `User` + `Guardian` |
| **Administrador da turma** | Responsável que criou a turma ou recebeu papel `admin`. Pode editar a turma, criar convites e confirmar pagamentos de qualquer evento. | `ClassMember.role = admin` |
| **Criador do evento** | Responsável que criou um evento. É automaticamente o "responsável pela arrecadação". Pode editar o evento e confirmar pagamentos. | `Event.created_by` / `Event.responsible` |
| **Administrador do sistema** | Equipe de operação. Usa o Django Admin (Unfold). **Fora do escopo do app mobile.** | `User.is_staff` |

> No app mobile, **todo usuário é um Responsável**. Papéis de admin de turma e de
> criador de evento são contextuais (variam por turma/evento), não papéis globais.

## Áreas da aplicação atual

1. **Área dos Pais** (server-side, será substituída/complementada pelo app Flutter):
   cadastro, login, turmas, eventos, pagamentos, participações, fornecedores, dashboard.
2. **Admin** (Django Unfold): CRUD completo de todas as entidades, estatísticas e
   gráficos. Continua existindo só na web; **não é exposto ao mobile**.

## Funcionalidades (catálogo completo)

### Conta e perfil
- Cadastro de responsável (com `class_code` opcional para já entrar numa turma).
- Login por e-mail e senha.
- Alteração de senha.
- Visualização e edição do perfil (dados do usuário + dados do responsável: CPF,
  chave PIX, nome do titular PIX, endereço, observações).
- Consulta da própria informação de PIX.

### Turmas
- Listar turmas das quais o responsável é membro.
- Criar turma (o criador vira `admin`). Gera `invite_code` único automaticamente.
- Ver detalhes da turma (membros, alunos, eventos recentes).
- Editar turma (admin).
- Entrar em turma por código de convite.
- Criar convite (genérico ou para um e-mail específico; envia e-mail se houver e-mail).
- Aceitar convite por token.

### Alunos
- Cadastrar aluno em uma turma (vinculado ao responsável logado).
- Editar/remover aluno (apenas alunos do próprio responsável).

### Eventos
- Listar eventos das turmas do responsável.
- Criar evento numa turma (tipos: arrecadação, lanche partilhado, presença).
- Ver detalhes do evento (itens, pagamentos, participações, progresso de arrecadação).
- Editar evento (admin ou criador).
- Encerrar evento.

### Itens do evento
- Adicionar item (despesa ou contribuição).
- Editar item.
- "Assumir" um item (atribuir a si).
- Marcar item como concluído.

### Pagamentos (eventos de arrecadação)
- Enviar pagamento com comprovante (imagem/PDF). Valor sugerido = valor individual ×
  nº de alunos do responsável na turma.
- Confirmar pagamento (admin/criador/responsável). Dispara e-mail ao pagador.
- Rejeitar pagamento (admin/criador/responsável). Dispara e-mail ao pagador.

### PIX
- Obter o código PIX "copia e cola" (BR Code EMV) do evento.
- Obter o QR Code PIX (imagem PNG / base64).

### Participações (lanche partilhado / presença)
- Confirmar participação (o que vai levar / quantas pessoas).
- Recusar participação (com motivo opcional).
- Cancelar participação confirmada.

### Fornecedores
- Listar fornecedores ativos, com busca por nome e filtro por categoria.
- Ver detalhes (com links prontos de WhatsApp, Instagram e Google Maps).
- Cadastrar/editar fornecedor.

### Dashboard
- Totais: turmas, alunos, eventos, eventos ativos.
- Total pago e quantidade de pagamentos pendentes do responsável.
- Gráfico de despesas mensais (últimos 12 meses).
- Próximos eventos.
- Aniversariantes do mês (alunos das turmas do responsável).

## Glossário

| Termo (pt-BR) | Termo no código | Significado |
|---------------|-----------------|-------------|
| Responsável | `Guardian` | Pai/mãe/responsável; perfil ligado ao usuário |
| Turma | `SchoolClass` | Grupo de alunos e responsáveis |
| Membro da turma | `ClassMember` | Vínculo responsável ↔ turma, com papel |
| Aluno | `Student` | Criança vinculada a um responsável e a uma turma |
| Convite | `ClassInvitation` | Convite para entrar numa turma (link/token ou e-mail) |
| Evento | `Event` | Atividade da turma (arrecadação/lanche/presença) |
| Item do evento | `EventItem` | Despesa ou contribuição dentro de um evento |
| Pagamento | `Payment` | Pagamento de um responsável para um evento |
| Participação | `EventParticipation` | Confirmação de presença/contribuição em evento |
| Arrecadação | `EventType.PAYMENT` | Evento que coleta dinheiro via PIX |
| Lanche Partilhado | `EventType.POTLUCK` | Cada um leva algo (potluck) |
| Confirmação de Presença | `EventType.PRESENCE` | Confirma quem vai e quantas pessoas |
| Fornecedor | `Supplier` | Contato útil (costureira, buffet, etc.) |
| Código de convite | `invite_code` | Código curto para entrar na turma |
| Chave PIX | `pix_key` | Chave PIX usada para receber pagamentos |
