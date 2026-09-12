# Nova Mecânica

Sistema de gestão para oficina mecânica, desenvolvido para auxiliar no gerenciamento dos processos e informações de uma oficina. O projeto foi desenvolvido utilizando Python e Django como parte da disciplina de Laboratório de Software 3.

**Deploy:** ainda não publicado
**Equipe:** [Rodrigo de Azevedo Junior 2840482421044 — 
João Gabriel Cardoso Martarello 2840482421028 — 
Felipe Delchiaro Malzoni 2840482421025 — 
Antônio de Brito Soares 2840482421035 c
Carlos Chen [RA] ] · Laboratório de Engenharia de Software · ADS Fatec Ribeirão Preto

## Stack

* **Frontend:** Django Templates / HTML, CSS e JavaScript
* **Backend:** Python 3.10+ / Django
* **Banco de dados:** PostgreSQL 14+ (SQLite disponível para testes)

## Como rodar localmente

### Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

* **Python 3.10 ou superior**
* **Git**
* **PostgreSQL 14 ou superior**

  * SQLite pode ser utilizado para testes rápidos, caso configurado no projeto.

### Passo a passo

1. Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd "Nova Mecanica"
```

2. Crie e ative o ambiente virtual:

**Windows — PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

Caso ocorra um erro de permissão no PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente.

Copie o arquivo `.env.example` para `.env`:

**Windows:**

```powershell
copy .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Preencha o arquivo `.env` com as configurações necessárias:

| Variável        | Descrição                                           |
| --------------- | --------------------------------------------------- |
| `SECRET_KEY`    | Chave secreta utilizada pelo Django                 |
| `DEBUG`         | Define se o modo de desenvolvimento está habilitado |
| `ALLOWED_HOSTS` | Hosts permitidos pela aplicação                     |
| `DB_ENGINE`     | Engine utilizada pelo banco de dados                |
| `DB_NAME`       | Nome do banco de dados                              |
| `DB_USER`       | Usuário do banco de dados                           |
| `DB_PASSWORD`   | Senha do banco de dados                             |
| `DB_HOST`       | Endereço do servidor do banco                       |
| `DB_PORT`       | Porta utilizada pelo banco                          |

Exemplo de configuração para PostgreSQL:

```env
SECRET_KEY=django-insecure-sua-chave-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=NovaMecDB
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres
DB_HOST=localhost
DB_PORT=5432
```

5. Crie o banco de dados no PostgreSQL.

O banco utilizado pelo exemplo acima é `NovaMecDB`. Ele pode ser criado pelo pgAdmin ou através do SQL:

```sql
CREATE DATABASE "NovaMecDB";
```

6. Execute as migrations:

```bash
python manage.py migrate
```

7. Crie um usuário administrador para acessar o Django Admin:

```bash
python manage.py createsuperuser
```

Siga as instruções exibidas no terminal para definir usuário, e-mail e senha.

8. Inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

9. Acesse a aplicação:

* **Aplicação:** `http://127.0.0.1:8000/`
* **Painel administrativo:** `http://127.0.0.1:8000/admin/`

## Estrutura do repositório

```text
Nova Mecanica/
├── core/                — App principal da aplicação
│   ├── models.py        — Modelos e estruturas de dados
│   ├── views.py         — Regras de controle das páginas
│   └── templates/       — Templates da aplicação
│
├── setup/               — Configurações globais do Django
│   ├── settings.py      — Configurações do projeto
│   └── urls.py          — Rotas principais
│
├── .venv/               — Ambiente virtual Python (não versionado)
├── .env                 — Variáveis de ambiente locais (não versionado)
├── .env.example         — Modelo das variáveis de ambiente
├── .gitignore           — Arquivos ignorados pelo Git
├── manage.py            — Utilitário de gerenciamento do Django
├── requirements.txt     — Dependências do projeto
└── README.md            — Documentação do projeto
```

## Convenções da equipe

* **Branches:** utilizar o padrão `feature/nome-da-feature` para novas funcionalidades.
* **Commits:** recomenda-se utilizar o padrão **Conventional Commits**.
* **Pull Requests:** toda PR deve passar pela revisão de pelo menos 1 integrante da equipe antes do merge.
* **Ambiente virtual:** sempre utilizar o `.venv` durante o desenvolvimento.
* **Variáveis de ambiente:** nunca versionar o arquivo `.env`.
* **Dependências:** ao adicionar uma nova biblioteca, atualizar o `requirements.txt`.

### Atualização do projeto

Após executar:

```bash
git pull
```

verifique se é necessário atualizar as dependências:

```bash
pip install -r requirements.txt
```

Caso tenham ocorrido alterações nos modelos do banco:

```bash
python manage.py migrate
```

Ao instalar uma nova dependência, atualize o arquivo:

```bash
pip freeze > requirements.txt
```

## Testes

Para executar os testes automatizados do Django:

```bash
python manage.py test
```

## Licença / Uso acadêmico

Projeto desenvolvido para a disciplina de **Laboratório de Software 3 — Laboratório de Engenharia de Software**, do curso de **Análise e Desenvolvimento de Sistemas (ADS)** da **Fatec Ribeirão Preto**, em 2026.

O projeto possui finalidade acadêmica.
