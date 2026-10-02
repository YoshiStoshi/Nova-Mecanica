/**
 * ==============================================================================
 * NOVA MECÂNICA - SCRIPT DE MONTAGEM DE ORÇAMENTO DINÂMICO (SPRINT 2)
 * Histórias: H10, H11, H12, H13, H14
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Obter dados serializados do template
    const veiculosData = window.ORCAMENTO_VEICULOS || [];
    const pecasData = window.ORCAMENTO_PECAS || [];
    const servicosData = window.ORCAMENTO_SERVICOS || [];

    // Elementos do DOM
    const selectCliente = document.getElementById('selectCliente');
    const selectVeiculo = document.getElementById('selectVeiculo');
    const veiculoHelpText = document.getElementById('veiculoHelpText');

    const tabelaPecasCorpo = document.getElementById('tabelaPecasCorpo');
    const tabelaServicosCorpo = document.getElementById('tabelaServicosCorpo');
    const pecasVaziaMsg = document.getElementById('pecasVaziaMsg');
    const servicosVaziaMsg = document.getElementById('servicosVaziaMsg');

    const btnAddPeca = document.getElementById('btnAddPeca');
    const btnAddServico = document.getElementById('btnAddServico');

    const inputDesconto = document.getElementById('inputDesconto');
    const rangeDesconto = document.getElementById('rangeDesconto');
    const erroDesconto = document.getElementById('erroDesconto');

    // Totais
    const spanSubtotalPecas = document.getElementById('subtotalPecas');
    const spanSubtotalServicos = document.getElementById('subtotalServicos');
    const spanSubtotalGeral = document.getElementById('subtotalGeral');
    const spanValorDesconto = document.getElementById('valorDesconto');
    const spanTotalFinal = document.getElementById('totalFinal');
    const btnConverterOS = document.getElementById('btnConverterOS');
    const formOrcamento = document.getElementById('formOrcamento');

    let contadorLinhasPeca = 0;
    let contadorLinhasServico = 0;

    // Formatador oficial BRL
    const formatadorBRL = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    function formatarMoeda(valor) {
        return formatadorBRL.format(valor || 0);
    }

    // ==========================================================================
    // 2. Filtro dinâmico de Veículos por Cliente selecionado
    // ==========================================================================
    function atualizarVeiculosDoCliente() {
        const clienteId = parseInt(selectCliente.value);
        selectVeiculo.innerHTML = '<option value="">-- Selecione o veículo --</option>';

        if (!clienteId) {
            selectVeiculo.disabled = true;
            veiculoHelpText.textContent = 'Selecione um cliente primeiro para visualizar os veículos.';
            return;
        }

        const veiculosDoCliente = veiculosData.filter(v => v.cliente_id === clienteId);

        if (veiculosDoCliente.length === 0) {
            selectVeiculo.disabled = true;
            veiculoHelpText.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-circle me-1"></i>Este cliente ainda não possui veículos cadastrados. <a href="/veiculos/novo/" target="_blank" class="fw-semibold">Cadastrar agora</a></span>';
        } else {
            selectVeiculo.disabled = false;
            veiculosDoCliente.forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.id;
                opt.textContent = `${v.placa} — ${v.marca} ${v.modelo} (${v.ano})`;
                selectVeiculo.appendChild(opt);
            });
            veiculoHelpText.textContent = `${veiculosDoCliente.length} veículo(s) encontrado(s) para este cliente.`;
            if (veiculosDoCliente.length === 1) {
                selectVeiculo.value = veiculosDoCliente[0].id;
            }
        }
    }

    selectCliente.addEventListener('change', atualizarVeiculosDoCliente);

    // ==========================================================================
    // 3. Adicionar Linha Dinâmica de Peça
    // ==========================================================================
    function adicionarLinhaPeca() {
        contadorLinhasPeca++;
        const rowId = `linha-peca-${contadorLinhasPeca}`;

        const tr = document.createElement('tr');
        tr.id = rowId;
        tr.className = 'linha-item-peca';

        // Opções do Select de Peças
        let opcoes = '<option value="">-- Selecione a peça --</option>';
        pecasData.forEach(p => {
            const estoqueBadge = p.estoque <= 0 ? ' (SEM ESTOQUE)' : ` (${p.estoque} un)`;
            opcoes += `<option value="${p.id}" data-preco="${p.preco}" data-estoque="${p.estoque}">${p.descricao} — R$ ${parseFloat(p.preco).toFixed(2)}${estoqueBadge}</option>`;
        });

        tr.innerHTML = `
            <td>
                <select name="pecas_id[]" class="form-select form-select-sm select-peca" required>
                    ${opcoes}
                </select>
            </td>
            <td style="width: 110px;">
                <input type="number" name="pecas_qtd[]" class="form-control form-control-sm text-center qtd-peca" min="1" value="1" required>
            </td>
            <td class="text-end font-mono preco-unit-peca text-muted" style="width: 130px;">
                R$ 0,00
            </td>
            <td class="text-end font-mono fw-semibold subtotal-peca text-primary" style="width: 140px;">
                R$ 0,00
            </td>
            <td class="text-center" style="width: 50px;">
                <button type="button" class="btn btn-outline-danger btn-sm p-1 border-0" title="Remover Peça" onclick="removerLinha('${rowId}', 'peca')">
                    <i class="bi bi-trash fs-6"></i>
                </button>
            </td>
        `;

        tabelaPecasCorpo.appendChild(tr);
        verificarTabelasVazias();
        vincularEventosLinha(tr);
        calcularTotais();
    }

    // ==========================================================================
    // 4. Adicionar Linha Dinâmica de Serviço
    // ==========================================================================
    function adicionarLinhaServico() {
        contadorLinhasServico++;
        const rowId = `linha-servico-${contadorLinhasServico}`;

        const tr = document.createElement('tr');
        tr.id = rowId;
        tr.className = 'linha-item-servico';

        let opcoes = '<option value="">-- Selecione o serviço --</option>';
        servicosData.forEach(s => {
            opcoes += `<option value="${s.id}" data-preco="${s.preco}">${s.descricao} — R$ ${parseFloat(s.preco).toFixed(2)}</option>`;
        });

        tr.innerHTML = `
            <td>
                <select name="servicos_id[]" class="form-select form-select-sm select-servico" required>
                    ${opcoes}
                </select>
            </td>
            <td style="width: 110px;">
                <input type="number" name="servicos_qtd[]" class="form-control form-control-sm text-center qtd-servico" min="1" value="1" required>
            </td>
            <td class="text-end font-mono preco-unit-servico text-muted" style="width: 130px;">
                R$ 0,00
            </td>
            <td class="text-end font-mono fw-semibold subtotal-servico text-primary" style="width: 140px;">
                R$ 0,00
            </td>
            <td class="text-center" style="width: 50px;">
                <button type="button" class="btn btn-outline-danger btn-sm p-1 border-0" title="Remover Serviço" onclick="removerLinha('${rowId}', 'servico')">
                    <i class="bi bi-trash fs-6"></i>
                </button>
            </td>
        `;

        tabelaServicosCorpo.appendChild(tr);
        verificarTabelasVazias();
        vincularEventosLinha(tr);
        calcularTotais();
    }

    // Vincular eventos 'change' e 'input' nos elementos da linha
    function vincularEventosLinha(row) {
        const select = row.querySelector('select');
        const qtdInput = row.querySelector('input[type="number"]');

        select.addEventListener('change', function () {
            atualizarSubtotalLinha(row);
            calcularTotais();
        });

        qtdInput.addEventListener('input', function () {
            if (parseInt(qtdInput.value) < 1 || isNaN(parseInt(qtdInput.value))) {
                qtdInput.value = 1;
            }
            atualizarSubtotalLinha(row);
            calcularTotais();
        });
    }

    function atualizarSubtotalLinha(row) {
        const select = row.querySelector('select');
        const qtdInput = row.querySelector('input[type="number"]');
        const precoTd = row.querySelector('.preco-unit-peca, .preco-unit-servico');
        const subtotalTd = row.querySelector('.subtotal-peca, .subtotal-servico');

        const selectedOption = select.options[select.selectedIndex];
        const preco = selectedOption && selectedOption.dataset.preco ? parseFloat(selectedOption.dataset.preco) : 0;
        const qtd = parseInt(qtdInput.value) || 0;
        const subtotalLinha = preco * qtd;

        precoTd.textContent = formatarMoeda(preco);
        subtotalTd.textContent = formatarMoeda(subtotalLinha);
    }

    // Remover linha
    window.removerLinha = function (rowId, tipo) {
        const row = document.getElementById(rowId);
        if (row) {
            row.remove();
            verificarTabelasVazias();
            calcularTotais();
        }
    };

    function verificarTabelasVazias() {
        const totalLinhasPecas = tabelaPecasCorpo.querySelectorAll('.linha-item-peca').length;
        const totalLinhasServicos = tabelaServicosCorpo.querySelectorAll('.linha-item-servico').length;

        pecasVaziaMsg.style.display = totalLinhasPecas === 0 ? 'block' : 'none';
        servicosVaziaMsg.style.display = totalLinhasServicos === 0 ? 'block' : 'none';
    }

    // ==========================================================================
    // 5. Cálculo em Tempo Real de Subtotais, Desconto e Total (H11)
    // ==========================================================================
    function calcularTotais() {
        let somaPecas = 0;
        let somaServicos = 0;

        // Somar todas as peças
        document.querySelectorAll('.linha-item-peca').forEach(row => {
            const select = row.querySelector('.select-peca');
            const qtdInput = row.querySelector('.qtd-peca');
            const selectedOpt = select.options[select.selectedIndex];
            if (selectedOpt && selectedOpt.dataset.preco) {
                const preco = parseFloat(selectedOpt.dataset.preco) || 0;
                const qtd = parseInt(qtdInput.value) || 0;
                somaPecas += (preco * qtd);
            }
        });

        // Somar todos os serviços
        document.querySelectorAll('.linha-item-servico').forEach(row => {
            const select = row.querySelector('.select-servico');
            const qtdInput = row.querySelector('.qtd-servico');
            const selectedOpt = select.options[select.selectedIndex];
            if (selectedOpt && selectedOpt.dataset.preco) {
                const preco = parseFloat(selectedOpt.dataset.preco) || 0;
                const qtd = parseInt(qtdInput.value) || 0;
                somaServicos += (preco * qtd);
            }
        });

        const subtotalGeral = somaPecas + somaServicos;

        // Validar e calcular desconto
        let percentualDesconto = parseFloat(inputDesconto.value);
        if (isNaN(percentualDesconto)) {
            percentualDesconto = 0;
        }

        let descontoInvalido = false;
        if (percentualDesconto < 0 || percentualDesconto > 100) {
            descontoInvalido = true;
            erroDesconto.style.display = 'block';
            inputDesconto.classList.add('is-invalid');
            btnConverterOS.disabled = true;
        } else {
            erroDesconto.style.display = 'none';
            inputDesconto.classList.remove('is-invalid');
            btnConverterOS.disabled = false;
        }

        // Derivar valor do desconto e total (duas casas decimais)
        const valorDesconto = Math.round(subtotalGeral * (percentualDesconto / 100) * 100) / 100;
        const totalFinal = Math.max(0, Math.round((subtotalGeral - valorDesconto) * 100) / 100);

        // Atualizar interface
        spanSubtotalPecas.textContent = formatarMoeda(somaPecas);
        spanSubtotalServicos.textContent = formatarMoeda(somaServicos);
        spanSubtotalGeral.textContent = formatarMoeda(subtotalGeral);
        spanValorDesconto.textContent = `- ${formatarMoeda(valorDesconto)}`;
        spanTotalFinal.textContent = formatarMoeda(totalFinal);
    }

    // Sincronizar campo de texto e slider de desconto
    inputDesconto.addEventListener('input', function () {
        let val = parseFloat(inputDesconto.value);
        if (!isNaN(val) && val >= 0 && val <= 100) {
            rangeDesconto.value = val;
        }
        calcularTotais();
    });

    rangeDesconto.addEventListener('input', function () {
        inputDesconto.value = rangeDesconto.value;
        calcularTotais();
    });

    // Eventos dos botões de adicionar linha
    btnAddPeca.addEventListener('click', adicionarLinhaPeca);
    btnAddServico.addEventListener('click', adicionarLinhaServico);

    // ==========================================================================
    // 6. Validação ao Submeter e Converter em OS (H12)
    // ==========================================================================
    formOrcamento.addEventListener('submit', function (e) {
        const clienteVal = selectCliente.value;
        const veiculoVal = selectVeiculo.value;

        if (!clienteVal || !veiculoVal) {
            e.preventDefault();
            alert('Por favor, selecione tanto o Cliente quanto o Veículo.');
            selectCliente.focus();
            return false;
        }

        const pecasLinhas = tabelaPecasCorpo.querySelectorAll('.linha-item-peca').length;
        const servicosLinhas = tabelaServicosCorpo.querySelectorAll('.linha-item-servico').length;

        if (pecasLinhas === 0 && servicosLinhas === 0) {
            e.preventDefault();
            alert('O orçamento deve conter pelo menos uma Peça ou um Serviço incluído.');
            return false;
        }

        // Validação de duplicados no front
        const pecasSelecionadas = [];
        let temDuplicata = false;
        tabelaPecasCorpo.querySelectorAll('.select-peca').forEach(s => {
            if (s.value) {
                if (pecasSelecionadas.includes(s.value)) {
                    temDuplicata = true;
                }
                pecasSelecionadas.push(s.value);
            }
        });

        const servicosSelecionados = [];
        tabelaServicosCorpo.querySelectorAll('.select-servico').forEach(s => {
            if (s.value) {
                if (servicosSelecionados.includes(s.value)) {
                    temDuplicata = true;
                }
                servicosSelecionados.push(s.value);
            }
        });

        if (temDuplicata) {
            e.preventDefault();
            alert('Atenção: Um mesmo item foi selecionado mais de uma vez. Ajuste a quantidade na mesma linha antes de converter.');
            return false;
        }

        // Desabilita botão para prevenir duplo clique
        btnConverterOS.disabled = true;
        btnConverterOS.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Gerando Ordem de Serviço...';
        return true;
    });

    // Iniciar com uma linha de peça e uma de serviço por conveniência
    adicionarLinhaPeca();
    adicionarLinhaServico();
});
