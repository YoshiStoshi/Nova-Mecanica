/**
 * ==============================================================================
 * NOVA MECÂNICA — GRÁFICOS DO DASHBOARD GERENCIAL (SPRINT 4 — E8)
 * Histórias: H19 (Faturamento Mensal), H20 (Top Serviços), H21 (Top Peças)
 * ==============================================================================
 */

document.addEventListener('DOMContentLoaded', function () {
    if (typeof Chart === 'undefined') {
        return;
    }

    const formatadorBRL = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
    });

    // 1. Gráfico de Faturamento Mensal Líquido (H19)
    const canvasFaturamento = document.getElementById('chartFaturamentoMensal');
    const dadosFaturamento = window.DASHBOARD_FATURAMENTO || { labels: [], faturamento: [], descontos: [] };

    if (canvasFaturamento && dadosFaturamento.labels.length > 0) {
        new Chart(canvasFaturamento, {
            type: 'bar',
            data: {
                labels: dadosFaturamento.labels,
                datasets: [
                    {
                        label: 'Faturamento Líquido (R$)',
                        data: dadosFaturamento.faturamento,
                        backgroundColor: 'rgba(30, 58, 138, 0.85)',
                        borderColor: '#1e3a8a',
                        borderWidth: 1,
                        borderRadius: 6,
                    },
                    {
                        label: 'Descontos Concedidos (R$)',
                        data: dadosFaturamento.descontos,
                        backgroundColor: 'rgba(239, 68, 68, 0.65)',
                        borderColor: '#ef4444',
                        borderWidth: 1,
                        borderRadius: 6,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return `${ctx.dataset.label}: ${formatadorBRL.format(ctx.parsed.y || 0)}`;
                            },
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return formatadorBRL.format(value);
                            },
                        },
                    },
                },
            },
        });
    }

    // 2. Gráfico Horizontal: Serviços Mais Executados (H20)
    const canvasServicos = document.getElementById('chartRankingServicos');
    const dadosServicos = window.DASHBOARD_SERVICOS || { labels: [], quantidades: [] };

    if (canvasServicos && dadosServicos.labels.length > 0) {
        new Chart(canvasServicos, {
            type: 'bar',
            data: {
                labels: dadosServicos.labels,
                datasets: [
                    {
                        label: 'Execuções Concluídas',
                        data: dadosServicos.quantidades,
                        backgroundColor: 'rgba(37, 99, 235, 0.8)',
                        borderColor: '#2563eb',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                    },
                },
            },
        });
    }

    // 3. Gráfico Horizontal: Peças Mais Vendidas (H21)
    const canvasPecas = document.getElementById('chartRankingPecas');
    const dadosPecas = window.DASHBOARD_PECAS || { labels: [], quantidades: [] };

    if (canvasPecas && dadosPecas.labels.length > 0) {
        new Chart(canvasPecas, {
            type: 'bar',
            data: {
                labels: dadosPecas.labels,
                datasets: [
                    {
                        label: 'Unidades Vendidas',
                        data: dadosPecas.quantidades,
                        backgroundColor: 'rgba(245, 158, 11, 0.85)',
                        borderColor: '#d97706',
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                    },
                },
            },
        });
    }
});

