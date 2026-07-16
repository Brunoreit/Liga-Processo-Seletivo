# Tech Stack

## Overview

A stack tecnológica foi escolhida considerando os objetivos do projeto, a aderência aos requisitos do MVP, a ampla adoção pelo mercado e as oportunidades de aprendizado em Engenharia de Software.

Como este é um projeto de longo prazo, algumas tecnologias poderão ser alteradas conforme a evolução do produto e novas necessidades identificadas durante o desenvolvimento.

---

## Front-end

| Tecnologia | Finalidade |
|------------|------------|
| React | Construção da interface do usuário |
| TypeScript | Tipagem estática e maior confiabilidade do código |
| Vite | Ambiente de desenvolvimento e build |
| Tailwind CSS | Estilização da aplicação |
| React Router | Gerenciamento de rotas |

---

## Back-end

| Tecnologia | Finalidade |
|------------|------------|
| Java 21 | Linguagem principal |
| Spring Boot | Desenvolvimento da API REST |
| Spring Security | Autenticação e autorização |
| Spring Data JPA | Persistência de dados |
| Hibernate | ORM |

---

## Banco de Dados

| Tecnologia | Finalidade |
|------------|------------|
| PostgreSQL | Banco de dados relacional |

---

## Autenticação

- JWT (JSON Web Token)
- Spring Security

---

## Comunicação

| Tecnologia | Finalidade |
|------------|------------|
| Resend | Envio de e-mails transacionais (confirmações, aprovações, comunicados, etc.) |

---

## Documentação

- OpenAPI / Swagger

---

## Testes

- JUnit
- Mockito

---

## DevOps

- Docker
- Docker Compose
- GitHub Actions (CI/CD)

---

## Deploy

| Camada | Tecnologia |
|--------|------------|
| Front-end | Vercel |
| Back-end | Railway |
| Banco de Dados | Railway PostgreSQL |

---

## Estrutura da Aplicação

O back-end seguirá uma arquitetura em camadas, separando responsabilidades entre apresentação, regras de negócio e acesso aos dados.

```text
Controller
    ↓
Service
    ↓
Repository
    ↓
Database
```

Essa organização tem como objetivo facilitar a manutenção, os testes e a evolução do sistema.