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
]
