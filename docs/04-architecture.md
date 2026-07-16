# Architecture

## Overview

A arquitetura do projeto foi planejada para priorizar simplicidade, organização e facilidade de manutenção, sem abrir mão de boas práticas de Engenharia de Software.

O sistema seguirá uma arquitetura cliente-servidor (Client-Server), com uma API REST responsável pelas regras de negócio e uma aplicação web responsável pela interface do usuário.

---

## High-Level Architecture

```text
                 +----------------------+
                 |      Front-end       |
                 |  React + TypeScript  |
                 +----------+-----------+
                            |
                        HTTP/REST
                            |
                 +----------v-----------+
                 |      Back-end        |
                 | Java + Spring Boot   |
                 +----------+-----------+
                            |
                 Spring Data JPA
                            |
                 +----------v-----------+
                 |    PostgreSQL        |
                 +----------------------+
```

---

## Architecture Style

O projeto utilizará uma arquitetura em camadas (Layered Architecture), separando responsabilidades entre apresentação, regras de negócio e acesso aos dados.

Essa abordagem facilita a manutenção, os testes e a evolução do sistema.

```text
HTTP Request
    ↓
Controller
    ↓
Service
    ↓
Repository
    ↓
Database
```

---

## Project Structure

A estrutura inicial do back-end seguirá a seguinte organização:

```text
src
└── main
    ├── controller
    ├── service
    ├── repository
    ├── entity
    ├── dto
    ├── config
    ├── security
    ├── exception
    └── util
```

A estrutura poderá evoluir conforme novas funcionalidades forem adicionadas.

---

## Front-end Architecture

O front-end será desenvolvido utilizando React e seguirá uma organização baseada em componentes reutilizáveis.

Estrutura inicial:

```text
src
├── components
├── pages
├── layouts
├── hooks
├── services
├── contexts
├── types
├── utils
└── assets
```

---

## API Design

A comunicação entre front-end e back-end será realizada por meio de uma API REST utilizando JSON.

Princípios adotados:

- Endpoints RESTful
- Versionamento da API (`/api/v1`)
- Autenticação baseada em JWT
- Respostas padronizadas
- Códigos HTTP apropriados

---

## Authentication

O acesso será baseado em autenticação utilizando JWT (JSON Web Token).

Perfis previstos:

- Candidato
- Organizador

As permissões serão controladas pelo Spring Security.

---

## Database

O sistema utilizará PostgreSQL como banco de dados relacional.

A modelagem seguirá princípios de normalização e integridade referencial.

O modelo completo será documentado em **05-database.md**.

---

## External Services

Serviços externos previstos:

- Resend (envio de e-mails)
- Railway (deploy)
- Vercel (frontend)

Novas integrações poderão ser adicionadas conforme a evolução do projeto.

---

## Architectural Principles

Durante o desenvolvimento serão priorizados os seguintes princípios:

- Separação de responsabilidades
- Código limpo e legível
- Componentização
- Reutilização de código
- Baixo acoplamento
- Alta coesão
- Facilidade de manutenção
- Escalabilidade