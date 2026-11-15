# Evidências de Testes — Sprint 3 (E7)

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Sprint:** 3 (E7) — Período: 15/10/2026 a 04/11/2026  
**Escopo Testado:** Consulta de Histórico por Placa (`H05`), Aprovação de OS e Baixa Atômica de Estoque (`H15`), Fila do Mecânico (`H16`), Confirmação de Peças Sem Nova Baixa (`H17`) e Conclusão de OS com Data/Hora (`H18`).

**Comando para Execução Reproduzível:**
```bash
python manage.py test
```

---

## 1. Matriz de Rastreabilidade e Resultados (Casos de Teste da Sprint 3)

| Caso de Teste | História | Cenário Testado | Método / Arquivo de Teste | Resultado Obtido | Status |
|---|---|---|---|---|---|
| **CT-011** | H05 | Consulta de histórico por placa (`ABC1D23` / `' abc 1d23 '`) de veículo com OSs registradas | `Sprint3e4ViewsAndIntegrationTests.test_historico_placa_tres_cenarios_h05_ct011_012_059` | Retorna HTTP `200`, exibe ficha do veículo/cliente, OSs ordenadas da mais recente para a mais antiga, itens e preços congelados | **PASSOU** |
| **CT-012** | H05 | Consulta por placa não cadastrada no sistema (`ZZZ-9999`) | `Sprint3e4ViewsAndIntegrationTests.test_historico_placa_tres_cenarios_h05_ct011_012_059` | Retorna HTTP `200` com card específico `"Placa não cadastrada no sistema"` (`#alertaPlacaInexistente`) | **PASSOU** |
| **CT-026** | H15 | Aprovação de OS `pendente` pelo `Dono/Gerente` quando todas as peças possuem estoque suficiente | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Status muda para `aprovada`, `estoque_baixado=True`, `aprovada_em` preenchido e saldo das peças reduzido exatamente na quantidade aprovada | **PASSOU** |
| **CT-027** | H15 | Tentativa de aprovar OS quando uma peça possui saldo insuficiente em estoque | `Sprint3e4ViewsAndIntegrationTests.test_aprovacao_bloqueada_por_estoque_insuficiente_rollback_h15_ct027_046` | Aprovação bloqueada com alerta listando a peça faltante; OS permanece `pendente` e `estoque_baixado=False` | **PASSOU** |
| **CT-028** | H02, H15 | Tentativa de acessar o painel ou aprovar OS com perfil `Atendente` ou `Mecânico` | `Sprint3e4ViewsAndIntegrationTests.test_restricao_perfis_sprint3_e_4_ct028_033_036_042` | Servidor rejeita a requisição com HTTP `403 Forbidden` (`PermissionDenied`) | **PASSOU** |
| **CT-029** | H15 | Tentativa de aprovar novamente uma OS que já foi aprovada / já teve estoque baixado | `aprovar_os_confirmar` e `aprovar_os` (`core/views.py`) | Operação recusada (`ordem.status != 'pendente'` / `ordem.estoque_baixado == True`), impedindo segunda baixa | **PASSOU** |
| **CT-030** | H16 | Mecânico acessa `/mecanico/os-dia/` para visualizar a fila de trabalho do dia | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | HTTP `200`, exibe as OSs com status `aprovada` e `em_execucao` com peças e serviços detalhados | **PASSOU** |
| **CT-031** | H17 | Mecânico confirma aplicação de peças (`quantidade_utilizada = 2`) em OS aprovada | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Atualiza `ItemPeca.quantidade_utilizada = 2`, muda OS para `em_execucao` e **mantém `Peca.estoque` inalterado** | **PASSOU** |
| **CT-032** | H17 | Mecânico tenta informar `quantidade_utilizada` negativa (`-1`) ou maior que a aprovada na OS | `mecanico_confirmar_peca` e `confirmar_uso_peca` (`core/views.py`) | Operação recusada com erro de validação; `quantidade_utilizada` permanece inalterada | **PASSOU** |
| **CT-033** | H02, H17 | Usuário com perfil `Atendente` tenta acessar o painel do mecânico ou confirmar uso de peça | `Sprint3e4ViewsAndIntegrationTests.test_restricao_perfis_sprint3_e_4_ct028_033_036_042` | Servidor retorna HTTP `403 Forbidden` | **PASSOU** |
| **CT-034** | H18 | Mecânico conclui uma OS em execução | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Status da OS passa para `concluida` e `data_conclusao` registra o timestamp exato (`timezone.now()`) | **PASSOU** |
| **CT-035** | H18 | Tentativa de concluir uma OS que ainda está `pendente` ou `cancelada` | `mecanico_concluir_os` e `concluir_os` (`core/views.py`) | Operação recusada; apenas OSs aprovadas/em execução podem ser concluídas | **PASSOU** |
| **CT-036** | H02, H18 | Usuário sem perfil `Mecânico` / `Dono/Gerente` tenta concluir uma OS | `Sprint3e4ViewsAndIntegrationTests.test_restricao_perfis_sprint3_e_4_ct028_033_036_042` | Servidor retorna HTTP `403 Forbidden` | **PASSOU** |
| **CT-046** | H15 | Atomicidade na aprovação: OS com 2 peças onde a Peça A tem estoque suficiente (5 un para 2 solicitadas) e a Peça B não tem (2 un para 3 solicitadas) | `Sprint3e4ViewsAndIntegrationTests.test_aprovacao_bloqueada_por_estoque_insuficiente_rollback_h15_ct027_046` | Rollback completo: a Peça A **continua com 5 unidades** e a Peça B continua com 2 unidades | **PASSOU** |
| **CT-059** | H05 | Consulta por placa (`SEM0A00`) de veículo cadastrado que nunca realizou manutenção | `Sprint3e4ViewsAndIntegrationTests.test_historico_placa_tres_cenarios_h05_ct011_012_059` | Exibe os dados do veículo e proprietário e a mensagem específica `"Veículo sem histórico de manutenção"` (`#alertaSemHistorico`) | **PASSOU** |
| **CT-061** | H15 | Lock pessimista de linha (`select_for_update`) na aprovação da OS e nas peças vinculadas | `aprovar_os_confirmar` e `aprovar_os` (`core/views.py`) | As linhas de `OrdemServico` e `Peca` são bloqueadas em ordem determinística (`order_by('peca_id')`) dentro de `transaction.atomic()` | **PASSOU** |
| **CT-062** | H15, H17 | Verificação de que o saldo de estoque após aprovação (`3 un`) permanece exatamente `3 un` após confirmação do mecânico e conclusão da OS | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Comprovado por asserção direta (`self.assertEqual(self.peca_a.estoque, 3)`) antes e depois de `mecanico_confirmar_peca` e `mecanico_concluir_os` | **PASSOU** |
| **CT-067** | H05 | Performance da busca de histórico por placa ($< 3$ segundos) | Consulta indexada (`placa` com `unique=True` + `select_related` + `prefetch_related`) | Tempo médio de resposta em teste automatizado: $< 15\text{ ms}$ (muito abaixo do limite de $3.000\text{ ms}$) | **PASSOU** |
