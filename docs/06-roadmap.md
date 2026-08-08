# Roadmap

## Overview

O desenvolvimento será realizado de forma incremental, priorizando entregas pequenas, funcionais e testáveis.

O projeto seguirá uma abordagem de fluxo vertical: cada domínio será desenvolvido até possuir uma funcionalidade utilizável antes de avançar para novas partes do sistema.

Este roadmap representa a direção geral do projeto e poderá ser ajustado conforme novas regras de negócio e necessidades forem descobertas durante o desenvolvimento.

---

# Fase 0 — Descoberta e Planejamento

## Objetivo

Compreender o problema e definir a base inicial do sistema.

## Principais atividades

- Levantamento de requisitos
- Conversas com organizações estudantis
- Definição do MVP
- Escolha da stack
- Definição da arquitetura inicial
- Modelagem inicial do banco
- Wireframes das principais telas
- Organização do repositório

## Resultado

Base conceitual e técnica necessária para iniciar o desenvolvimento.

---

# Fase 1 — Estrutura Inicial

## Objetivo

Criar a infraestrutura base da aplicação.

## Principais atividades

- Backend Django + Django REST Framework
- Frontend React
- PostgreSQL
- Docker
- Estruturação dos apps do backend
- Integração inicial entre os serviços
- Configuração inicial do projeto

## Resultado

Aplicação executando com frontend, backend e banco de dados.

---

# Fase 2 — Usuários e Autenticação

## Objetivo

Criar o fluxo principal de usuários da plataforma.

## Principais atividades

- Model de usuário
- Cadastro
- Login com JWT
- Refresh token
- Consulta do usuário autenticado
- Atualização de perfil
- Controle inicial de permissões

## Pendente / evolução futura

- Recuperação de senha
- Refinamentos de perfil

## Resultado

Usuário consegue criar conta, autenticar-se e gerenciar seus dados básicos.

---

# Fase 3 — Núcleo do Processo Seletivo

## Objetivo

Construir o primeiro fluxo completo de um processo seletivo.

### 3.1 — Processo Seletivo

- Model e migration
- Administração pelo Django Admin
- Criação
- Listagem
- Consulta individual
- Atualização
- Exclusão somente em rascunho
- Permissões administrativas
- Visibilidade de processos publicados
- Ciclo de vida:
  - Draft
  - Published
  - Closed
- Registro automático de publicação

### 3.2 — Etapas

- Modelar etapas
- Relacionar etapas ao processo seletivo
- Definir ordem das etapas
- Criar/listar etapas
- Editar etapas
- Excluir etapas
- Impedir alterações estruturais quando necessário
- Integrar etapas ao detalhe do processo seletivo

### 3.3 — Inscrições

- Modelar inscrição
- Relacionar candidato e processo seletivo
- Criar inscrição
- Impedir inscrição duplicada
- Respeitar período de inscrições
- Consultar inscrições do candidato
- Consultar candidatos inscritos pelo organizador

### 3.4 — Fluxo do Processo

- Associar candidato às etapas
- Controlar avanço entre etapas
- Status da inscrição
- Histórico do candidato no processo

## Resultado esperado

Fluxo:

Processo Seletivo
→ Etapas
→ Inscrição
→ Acompanhamento do candidato

funcionando de ponta a ponta.

---

# Fase 4 — Primeiro Frontend Funcional

## Objetivo

Transformar o fluxo já existente no backend em uma experiência utilizável.

## Principais atividades

- Login e cadastro
- Perfil do candidato
- Listagem de processos seletivos
- Detalhe de processo
- Inscrição
- Área "Minhas inscrições"
- Interface administrativa inicial
- Criação e edição de processos
- Configuração de etapas

## Resultado esperado

Primeiro fluxo vertical completo utilizável através da interface.

---

# Fase 5 — Avaliações

## Objetivo

Permitir avaliação dos candidatos durante as etapas.

## Principais atividades

- Registrar avaliações
- Notas
- Observações
- Avaliadores
- Histórico de avaliações
- Aprovação/reprovação
- Movimentação entre etapas

## Resultado esperado

Organizadores conseguem conduzir o processo seletivo dentro da plataforma.

---

# Fase 6 — Comunicação

## Objetivo

Automatizar a comunicação com candidatos.

## Principais atividades

- Confirmação de inscrição
- Convocação para etapas
- Aprovação/reprovação
- Resultado final
- Comunicados gerais
- Templates de e-mail

## Resultado esperado

Redução do trabalho manual de comunicação da organização.

---

# Fase 7 — Qualidade e Produção

## Objetivo

Preparar o sistema para utilização real.

## Principais atividades

- Testes automatizados
- Tratamento de erros
- Validações adicionais
- Segurança
- CI/CD
- Deploy
- Monitoramento básico
- Revisão de UX
- Testes do fluxo completo

## Resultado esperado

MVP estável e disponível em produção.

---

# Fase 8 — MVP

## Critérios

- Cadastro e autenticação
- Perfil do candidato
- Processo seletivo
- Etapas
- Inscrições
- Fluxo dos candidatos
- Dashboard do candidato
- Dashboard do organizador
- Avaliações
- Comunicação por e-mail
- Deploy em produção

## Resultado esperado

Primeira utilização real da plataforma pela Liga de TI.

---

# Aprendizados Esperados

- Desenvolvimento Full Stack
- APIs REST
- Django e Django REST Framework
- React
- PostgreSQL
- Docker
- Git e GitHub
- Arquitetura de Software
- Modelagem de domínio
- Testes
- CI/CD
- Deploy
- Engenharia de Software