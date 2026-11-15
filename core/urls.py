from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard & Autenticação
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Clientes
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/novo/', views.cliente_criar, name='cliente_criar'),

    # Veículos
    path('veiculos/', views.veiculos, name='veiculos'),
    path('veiculos/novo/', views.veiculo_criar, name='veiculo_criar'),
    path('api/veiculos/cliente/<int:cliente_id>/', views.api_veiculos_por_cliente, name='api_veiculos_cliente'),

    # Catálogo (Dono/Gerente) - Sprint 1 e Sprint 2
    path('catalogo/pecas/', views.pecas_list_form, name='pecas'),
    path('catalogo/pecas/<int:pk>/ajustar-estoque/', views.peca_ajustar_estoque, name='peca_ajustar_estoque'),
    path('catalogo/pecas/<int:pk>/excluir/', views.peca_excluir, name='peca_excluir'),
    path('catalogo/servicos/', views.servicos_list_form, name='servicos'),
    path('catalogo/servicos/<int:pk>/excluir/', views.servico_excluir, name='servico_excluir'),

    # Orçamentos - Sprint 2
    path('orcamentos/novo/', views.orcamento_novo, name='orcamento_novo'),
    path('orcamentos/converter/', views.orcamento_converter, name='orcamento_converter'),

    # Ordens de Serviço (João)
    path('ordens/', views.ordens, name='ordens'),
    path('ordens/<int:pk>/', views.ordem_detalhe, name='ordem_detalhe'),
    path('ordens/<int:pk>/status/', views.ordem_alterar_status, name='ordem_alterar_status'),
    path('ordens/<int:pk>/desconto/', views.ordem_desconto, name='ordem_desconto'),
    path('ordens/<int:pk>/pecas/adicionar/', views.ordem_item_adicionar, {'tipo': 'peca'}, name='ordem_peca_adicionar'),
    path('ordens/<int:pk>/servicos/adicionar/', views.ordem_item_adicionar, {'tipo': 'servico'}, name='ordem_servico_adicionar'),
    path('ordens/<int:pk>/pecas/<int:item_id>/remover/', views.ordem_item_remover, {'tipo': 'peca'}, name='ordem_peca_remover'),
    path('ordens/<int:pk>/servicos/<int:item_id>/remover/', views.ordem_item_remover, {'tipo': 'servico'}, name='ordem_servico_remover'),

    # Sprint 3 (E7): Aprovação Atômica de OS, Histórico por Placa e Painel do Mecânico
    path('os/aprovar/', views.aprovar_os_painel, name='aprovar_os_painel'),
    path('os/<int:pk>/aprovar-painel/', views.aprovar_os_painel, name='aprovar_os_detalhe'),
    path('os/<int:pk>/aprovar/', views.aprovar_os_confirmar, name='os_aprovar'),
    path('veiculos/historico/', views.historico_placa, name='historico_placa'),
    path('mecanico/os-dia/', views.mecanico_os_dia, name='mecanico_os_dia'),
    path('mecanico/os/<int:pk>/pecas/<int:item_id>/confirmar/', views.mecanico_confirmar_peca, name='mecanico_confirmar_peca'),
    path('mecanico/os/<int:pk>/concluir/', views.mecanico_concluir_os, name='mecanico_concluir_os'),

    # Sprint 4 (E8): Dashboard Gerencial e Relatórios (H19, H20, H21)
    path('relatorios/dashboard/', views.relatorios_dashboard, name='relatorios_dashboard'),

    # Rotas de API / Endpoints Transacionais Consolidados (Felipe — Sprints 1 a 4)
    path('sprint1/catalogo/pecas/', views.catalogo_pecas, name='sprint1_pecas'),
    path('sprint1/catalogo/servicos/', views.catalogo_servicos, name='sprint1_servicos'),
    path('sprint1/catalogo/pecas/<int:pk>/excluir/', views.excluir_peca_sem_vinculo, name='sprint1_excluir_peca'),
    path('sprint1/catalogo/servicos/<int:pk>/excluir/', views.excluir_servico_sem_vinculo, name='sprint1_excluir_servico'),
    path('sprint2/orcamentos/converter/', views.converter_orcamento_em_os, name='sprint2_converter_orcamento'),
    path('sprint2/pecas/<int:pk>/estoque/', views.ajustar_estoque_api, name='sprint2_ajustar_estoque'),
    path('sprint2/pecas/<int:pk>/excluir/', views.excluir_peca_protegida_api, name='sprint2_excluir_peca'),
    path('sprint3/ordens/<int:pk>/aprovar/', views.aprovar_os, name='sprint3_aprovar_os'),
    path('sprint3/ordens/<int:pk>/pecas/<int:item_id>/uso/', views.confirmar_uso_peca, name='sprint3_confirmar_uso'),
    path('sprint3/ordens/<int:pk>/concluir/', views.concluir_os, name='sprint3_concluir_os'),
    path('sprint4/relatorios/faturamento-mensal/', views.faturamento_mensal, name='sprint4_faturamento_mensal'),
]
