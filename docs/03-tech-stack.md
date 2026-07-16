# Tech Stack

## Overview

A stack tecnológica foi definida considerando três fatores principais:

- Compatibilidade com o ecossistema de projetos da Liga de TI;
- Facilidade de manutenção e futura integração com outras plataformas da organização;
- Oportunidade de aprendizado em desenvolvimento Full Stack e Engenharia de Software.

O sistema será desenvolvido como uma aplicação web baseada em uma arquitetura cliente-servidor, utilizando uma API REST para comunicação entre o front-end e o back-end.

---

## Stack

### Backend

- Python 3.12
- Django 5
- Django REST Framework
- Simple JWT
- PostgreSQL

**Responsabilidades**

- API REST
- Regras de negócio
- Autenticação e autorização
- Persistência de dados
- Envio de e-mails
- Administração do sistema

---

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Query
- React Router

**Responsabilidades**

- Interface do usuário
- Consumo da API
- Gerenciamento de estado do servidor
- Navegação entre páginas
- Componentização da interface

---

### Infraestrutura

#### Desenvolvimento

- Docker Desktop
- Docker Compose

#### Produção

- Railway

---

### Banco de Dados

- PostgreSQL 16+

---

### Autenticação

- JWT (Simple JWT)

---

### Comunicação

#### Desenvolvimento

- Console Email Backend (Django)

#### Produção

- Resend

---

## Requisitos

### Utilizando Docker

- Docker Desktop
- Docker Compose

### Sem Docker

- Python 3.12
- Node.js 20+
- PostgreSQL 16+

---

## Estrutura Geral

```text
Frontend (React)
        │
        │ HTTP / REST
        ▼
Backend (Django REST Framework)
        │
        ▼
PostgreSQL
```

---

## Motivação das Escolhas

| Tecnologia | Motivo |
|------------|--------|
| React | Interface moderna baseada em componentes reutilizáveis. |
| TypeScript | Maior segurança, tipagem estática e facilidade de manutenção. |
| Django | Framework com excelente produtividade e organização do projeto. |
| Django REST Framework | Construção de APIs REST seguindo boas práticas. |
| PostgreSQL | Banco relacional robusto, ideal para o domínio do projeto. |
| Docker | Padroniza o ambiente de desenvolvimento e simplifica o deploy. |
| Railway | Plataforma simples para publicação da aplicação. |
| Resend | Serviço para envio de e-mails transacionais durante o processo seletivo. |

---

## Observações

Esta stack foi escolhida para manter compatibilidade com outros sistemas desenvolvidos pela Liga de TI, permitindo o compartilhamento de conhecimento, infraestrutura e futuras integrações entre projetos.

Algumas tecnologias poderão ser revisadas conforme a evolução do produto e novos requisitos forem identificados.