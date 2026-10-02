# João — Sprints 1 e 2: escopo corrigido

**Status:** implementação parcial aguardando integração com as partes dos colegas.
**Branch:** `joao-sprint1e2`.

## O que permanece nesta entrega

- H03/H04: formulários, validação de CPF/placa e controllers de cadastro/listagem.
- H22: templates Bootstrap de login e cadastros, erros por campo e retenção dos dados.
- H11: cálculo decimal e desconto de 0% a 100%, mantidos com João por confirmação expressa dele.
- H13/H14: controllers e operações de inclusão/remoção de itens na OS, sem baixa de estoque.
- Testes das funcionalidades de João.

## O que foi retirado

Foram restaurados ao estado original da `main`: `core/models.py`, `core/admin.py`, `core/views.py`, `core/urls.py`, `core/tests.py`, `setup/settings.py`, `templates/base.html`, `templates/core/home.html` e `README.md`.

Foram removidos a migração `0001_initial.py` e o comando de criação/configuração de perfis. Não há criação de modelos, constraints, migrações, seeds de homologação ou implementação de autenticação nesta entrega. As fixtures de usuários/dados nos testes são somente para exercitar os próprios controllers em banco de teste.

As funções de João ficaram em `core/views_joao.py`. O módulo `core/urls_joao.py` contém exclusivamente as rotas dessas funções; ele **não está registrado** na configuração principal, que permanece com Rodrigo. Isso permite iniciar o esqueleto original sem tentar importar modelos que ainda não existem.

## Dependências de integração

Os arquivos de formulário/controller/serviço ainda referenciam modelos a serem entregues pelos colegas. Eles não funcionam isoladamente e não devem ser apresentados como um incremento já integrado ou pronto para deploy.

- **Antônio/Chen:** definir modelos, tabelas, migrações e restrições. O contrato usado pelo código de João deve ser conferido com eles; não foi implementado nesta correção.
- **Felipe:** implementar autenticação e perfis/permissões. `core/forms_login.py` apenas aplica Bootstrap ao `AuthenticationForm` do Django; não cria sessões, contas, grupos ou rotas. Pode ser escolhido como formulário pela view de login do colega.
- **Rodrigo:** integrar as rotas próprias de João à lista de rotas de `core`, configurar o login e a navegação no template base. Fazer isso depois de os modelos estarem disponíveis. Os templates usam os nomes `core:clientes`, `core:veiculos`, `core:ordens` e as demais rotas declaradas em `core/urls_joao.py`.

### Contrato provisório dos modelos usados pelo código

Este quadro documenta os nomes atualmente referenciados, não atribui sua implementação a João. Se os modelos entregues pelos colegas usarem outros nomes, ajustar **os formulários/controllers de João** para consumir os modelos reais.

| Modelo esperado em `core.models` | Campos/relações usados |
| --- | --- |
| Cliente | `nome`, `cpf`, `telefone`, `email`; CPF único e normalizado. |
| Veiculo | `cliente`, `placa`, `marca`, `modelo`, `ano`; placa única e normalizada. |
| Peca / Servico | `descricao`, `preco`; peça tem `estoque`, somente lido nos testes. |
| OrdemServico | `cliente`, `veiculo`, `status`, `desconto_percentual`, `subtotal`, `valor_desconto`, `total`; reversos `itens_peca` e `itens_servico`. |
| ItemPeca / ItemServico | `ordem`, `peca` ou `servico`, `quantidade`, `preco_unitario_historico`; propriedade `subtotal` para exibição. |

O preço histórico foi nomeado `preco_unitario_historico` conforme o checklist. Os nomes das tabelas associativas e suas constraints são responsabilidade dos colegas do banco. Os controllers assumem quantidade positiva, preço não negativo, chaves estrangeiras válidas e unicidade de cada item por OS; essas restrições ainda precisam existir nos modelos/banco.

As operações de edição exigem OS `pendente`, permissões Django correspondentes, POST e CSRF. Cada alteração usa transação, copia o preço do catálogo para o vínculo e recalcula o total. Nenhuma delas aprova a OS ou baixa estoque.

### H11

`core.calculos.calcular_totais` recebe pares `(quantidade, preco_unitario)` e o desconto, usando `Decimal` ou strings decimais. Retorna subtotal, valor do desconto e total com duas casas decimais. O total usa `ROUND_HALF_UP`. Não existe modelo ou fluxo de conversão de orçamento nesta entrega; a função poderá ser consumida pelo módulo responsável por ele.

## Validação atual

```bash
python manage.py check
python manage.py test core.test_joao --verbosity 2
```

- Verificação Django: sem problemas.
- **7 testes passaram:** cálculo decimal, limites/arredondamento, entradas monetárias inválidas e validação/normalização de CPF e placa.
- **21 testes de integração foram ignorados explicitamente (`skipped`)** porque os modelos dos colegas ainda não existem. Não contam como aprovados. Quando os modelos existirem, esses testes serão habilitados; também será necessário integrar as rotas e autenticação.
- Não foram validados os fluxos completos, PostgreSQL, concorrência ou deploy desta versão corrigida.

A evidência anterior de 28 testes aprovados e revisão visual era da versão com escopo ampliado e **não se aplica a esta correção**.

O banco SQLite de demonstração local da versão anterior não foi alterado ou apagado. Ele contém o esquema removido do código. Para integrar futuras migrações, preparar um banco de desenvolvimento novo junto com os responsáveis pelo banco.

## Corrigir a branch já enviada

O commit anterior `64c107a` continua no histórico. Esta correção está na árvore de trabalho local, sem commit/push. Fazer um novo commit corretivo preserva o histórico; não é necessário reset nem push forçado.

Na cópia local indicada no guia, revisar `git diff` e então:

```bash
git add -A core setup/settings.py templates README.md docs
git commit -m "fix: restringe entrega ao escopo de Joao"
git push origin joao-sprint1e2
```

Se já existir um PR dessa branch, o novo push atualiza o mesmo PR. A descrição deve dizer que os módulos aguardam os modelos e a integração dos colegas, e informar **7 testes aprovados e 21 pendentes**, em vez de 28 aprovados.
