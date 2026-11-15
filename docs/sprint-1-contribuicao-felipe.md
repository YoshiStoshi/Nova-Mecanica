# Relatório Individual de Contribuição — Sprint 1 (E5)

**Aluno:** Felipe Delchiaro Malzoni  
**RA:** 2840482421025  
**Projeto:** Nova Mecânica  
**Sprint:** 1 (E5) · **Período:** 21/08/2026 a 22/09/2026  
**Papel nesta sprint:** Desenvolvedor Backend / Autenticação, Permissões e Catálogos  

---

## 1. O que fiz

| Item | Arquivo | Status |
|---|---|---|
| Implementei a verificação de perfil para usuários Dono/Gerente, Atendente e Mecânico (`usuario_tem_perfil`). | `core/views.py` | Concluído |
| Criei o decorator `exigir_perfil`, combinando `@login_required` com validação de grupos Django. | `core/views.py` | Concluído |
| Bloqueei o acesso direto às URLs quando o usuário não possui o perfil exigido, lançando `PermissionDenied`. | `core/views.py` | Concluído |
| Implementei a listagem, busca e criação de peças por meio de `PecaForm` (`catalogo_pecas`). | `core/views.py` | Concluído |
| Implementei a listagem, busca e criação de serviços por meio de `ServicoForm` (`catalogo_servicos`). | `core/views.py` | Concluído |
| Restrigi as operações dos catálogos ao perfil Dono/Gerente (`H06`, `H07`). | `core/views.py` | Concluído |
| Implementei a exclusão protegida de peças e serviços sem vínculo com itens de OS (`excluir_peca_sem_vinculo`, `excluir_servico_sem_vinculo`). | `core/views.py` | Concluído |
| Criei as rotas do catálogo e realizei a consolidação direta em `core/urls.py`. | `core/urls.py` | Concluído |

- **Evidências no Repositório:** Commit `4a8fb8a` (`origin/Features/Felipe`), integrado na branch `main` via `PR #5` (`890c859`).

---

## 2. Rituais que participei

- [x] Dailies/weeklies — Alinhamento de permissões de grupos e rotas do catálogo
- [x] Sprint Review — Validação das telas e bloqueios de acesso por perfil (H01, H02, H06, H07)
- [x] Retrospectiva — Consolidação do roteamento em `core/urls.py`

---

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| `PR #2` / `PR #3` | João Gabriel / Rodrigo | Verificação de compatibilidade entre `PecaForm`, `ServicoForm`, grupos de permissão e templates `catalogo/`. |

---

## 4. Dificuldades e o que aprendi

A principal preocupação foi não depender apenas da interface para proteger os catálogos. Por isso, a autorização foi colocada no backend, usando `login_required` e um decorator próprio para conferir os grupos do usuário. Também foi necessário separar a regra de exclusão da peça ou serviço: o item pode ser removido somente quando não existe vínculo histórico com uma Ordem de Serviço. O uso de `transaction.atomic()` nas criações mantém a gravação consistente e as URLs separadas em `sprint1_urlpatterns` facilitam a integração com o projeto existente.

---

## 5. Status de Integração no Projeto

Todas as views e decorators inicialmente prototipados em `sprint1_backend.py` foram consolidados na estrutura oficial da aplicação Django em `core/views.py` e roteados diretamente em `core/urls.py`.

Os grupos `Dono/Gerente`, `Atendente` e `Mecânico` são provisionados pelo comando `python manage.py setup_perfis` e os templates `templates/catalogo/pecas_list_form.html` e `templates/catalogo/servicos_list_form.html` estão integrados.
