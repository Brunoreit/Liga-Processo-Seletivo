# Architecture

## Overview

A arquitetura do projeto foi planejada para priorizar simplicidade, organização e facilidade de manutenção, sem abrir mão de boas práticas de Engenharia de Software.

O sistema seguirá uma arquitetura cliente-servidor (Client-Server), composta por uma aplicação React responsável pela interface do usuário e uma API REST desenvolvida em Django REST Framework responsável pelas regras de negócio e acesso aos dados.

A arquitetura também busca manter compatibilidade com outros projetos da Liga de TI, facilitando futuras integrações e reutilização de componentes.

---

## High-Level Architecture

```text
                 +----------------------+
                 |      Front-end       |
                 | React + TypeScript   |
                 +----------+-----------+
                            |
                        HTTP / REST
                            |
                 +----------v-----------+
                 |      Back-end        |
                 | Django REST API      |
                 +----------+-----------+
                            |
                      Django ORM
                            |
                 +----------v-----------+
                 |    PostgreSQL        |
                 +----------------------+
```

---

## Architecture Style

O projeto utilizará uma arquitetura em camadas (Layered Architecture), separando responsabilidades entre interface, regras de negócio e persistência de dados.

Embora o Django já forneça uma estrutura organizada por padrão, o projeto buscará manter uma separação clara entre responsabilidades para facilitar manutenção, testes e evolução do sistema.

Fluxo simplificado de uma requisição:

```text
HTTP Request
      ↓
APIView / ViewSet
      ↓
Service (Business Rules)
      ↓
Model / ORM
      ↓
PostgreSQL
```

---

## Backend Architecture

O back-end será organizado utilizando o conceito de **Django Apps**, onde cada domínio da aplicação será responsável por concentrar suas próprias regras de negócio.

Estrutura inicial prevista:

```text
backend/

apps/
├── users/
├── selection/
├── organizations/
├── notifications/

core/
config/
```

Cada App poderá conter sua própria organização interna, incluindo:

```text
users/

models.py
views.py
serializers.py
services.py
permissions.py
urls.py
tests.py
```

Essa abordagem favorece modularidade e facilita a evolução do sistema conforme novos módulos forem adicionados.

---

## Front-end Architecture

O front-end será desenvolvido utilizando React e seguirá uma arquitetura baseada em componentes reutilizáveis.

Estrutura inicial:

```text
src/

api/
components/
hooks/
layouts/
pages/
services/
types/
utils/
assets/
```

Responsabilidades principais:

- **Pages:** composição das telas.
- **Components:** componentes reutilizáveis.
- **Hooks:** lógica de comunicação com a API utilizando React Query.
- **API/Services:** centralização das chamadas HTTP.
- **Types:** tipagens TypeScript compartilhadas.

---

## API Design

A comunicação entre front-end e back-end ocorrerá através de uma API REST utilizando JSON.

Princípios adotados:

- Endpoints RESTful
- Versionamento da API (`/api/v1`)
- Serialização utilizando Django REST Framework
- Autenticação baseada em JWT
- Respostas padronizadas
- Utilização adequada dos códigos HTTP

---

## Authentication

A autenticação será baseada em JWT (JSON Web Token), utilizando a biblioteca **Simple JWT**.

Perfis inicialmente previstos:

- Candidato
- Organizador

As permissões serão controladas através do sistema de autenticação e permissões do Django REST Framework.

---

## Database

O sistema utilizará PostgreSQL como banco de dados principal.

O acesso aos dados será realizado através do Django ORM.

A modelagem seguirá princípios de normalização e integridade referencial.

O modelo completo será documentado em **05-database.md**.

---

## External Services

Serviços externos previstos:

- Resend (envio de e-mails em produção)
- Railway (deploy do back-end e banco de dados)
- Vercel (deploy do front-end)

Durante o desenvolvimento, o envio de e-mails utilizará o Console Email Backend do Django.

Novas integrações poderão ser adicionadas conforme a evolução do projeto.

---

## Architectural Principles

Durante o desenvolvimento serão priorizados os seguintes princípios:

- Separação de responsabilidades
- Modularização por domínio (Django Apps)
- Código limpo e legível
- Componentização da interface
- Reutilização de código
- Baixo acoplamento
- Alta coesão
- Facilidade de manutenção
- Escalabilidade