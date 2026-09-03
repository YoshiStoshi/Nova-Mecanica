# 🛠️ Nova Mecanica

Trabalho prático para a matéria de **Laboratório de Software 3**.  
Sistema de gestão para oficina mecânica desenvolvido utilizando **Python** e **Django**.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
- **Python 3.10 ou superior**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/)
- **PostgreSQL 14** (ou SQLite para testes rápidos): [Download PostgreSQL](https://www.postgresql.org/download/)

---

## 🚀 Passo a Passo para Executar o Projeto

Siga os passos abaixo para configurar e rodar o projeto na sua máquina local:

### 1. Clonar o Repositório
Abra o terminal (Prompt de Comando ou PowerShell) e rode:
```bash
git clone <URL_DO_REPOSITORIO>
cd "Nova Mecanica"
```

---

### 2. Criar e Ativar o Ambiente Virtual (`.venv`)

O ambiente virtual isola as dependências do projeto para evitar conflitos na sua máquina.

- **No Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate
  ```
  *(Se ocorrer erro de permissão no PowerShell, execute primeiro: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **No Linux ou macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

> 💡 **Nota:** Ao ativar com sucesso, o identificador `(.venv)` aparecerá no início da linha do seu terminal.

---

### 3. Instalar as Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias do projeto:
```bash
pip install -r requirements.txt
```

---

### 4. Configurar as Variáveis de Ambiente (`.env`)

Copie o arquivo de exemplo `.env.example` para criar o seu arquivo `.env`:

- **No Windows (CMD/PowerShell):**
  ```powershell
  copy .env.example .env
  ```
- **No Linux ou macOS:**
  ```bash
  cp .env.example .env
  ```

Abra o arquivo `.env` gerado e verifique se as credenciais do seu banco de dados estão corretas:

```env
SECRET_KEY=django-insecure-sua-chave-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1, localhost

# Para PostgreSQL:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=NovaMecDB
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres
DB_HOST=localhost
DB_PORT=5432
```

> 📌 **Importante:** Certifique-se de que o banco de dados `NovaMecDB` já foi criado no seu PostgreSQL (via pgAdmin ou comando SQL `CREATE DATABASE "NovaMecDB";`).

---

### 5. Aplicar as Migrações no Banco de Dados

Rode o comando abaixo para criar as tabelas no banco de dados:
```bash
python manage.py migrate
```

---

### 6. Criar um Usuário Administrador (Superusuário)

Para ter acesso ao painel administrativo do Django:
```bash
python manage.py createsuperuser
```
Preencha o nome de usuário, e-mail e senha conforme instruído no terminal.

---

### 7. Iniciar o Servidor de Desenvolvimento

Agora basta iniciar o servidor local:
```bash
python manage.py runserver
```

Acesse no seu navegador:
- **Aplicação Principal:** `http://127.0.0.1:8000/`
- **Painel Administrativo:** `http://127.0.0.1:8000/admin/`

---

## 📁 Estrutura do Projeto

```text
Nova Mecanica/
├── .venv/               # Ambiente virtual com pacotes Python (não vai pro Git)
├── core/                # App principal da aplicação (models, views, templates)
├── setup/               # Configurações globais do Django (settings.py, urls.py)
├── .env                 # Suas variáveis de ambiente locais (não vai pro Git)
├── .env.example         # Modelo para criação do arquivo .env
├── .gitignore           # Arquivos ignorados pelo Git
├── manage.py            # Utilitário de linha de comando do Django
├── README.md            # Documentação e guia do projeto
└── requirements.txt     # Lista de dependências Python do projeto
```

---

## 💡 Dicas para o Trabalho em Grupo (Git & Django)

1. **Sempre ative o `.venv`** antes de começar a trabalhar no projeto.
2. **Ao atualizar o código do Git (`git pull`):**
   - Se novos pacotes foram adicionados, rode: `pip install -r requirements.txt`
   - Se as tabelas/modelos foram alterados, rode: `python manage.py migrate`
3. **Ao instalar um novo pacote (`pip install nome-do-pacote`):**
   - Atualize a lista de dependências para o grupo rodando: `pip freeze > requirements.txt`
4. **Nunca suba o arquivo `.env` para o Git.** Ele contém senhas e chaves locais e já está configurado no `.gitignore`.
