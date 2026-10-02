from django.urls import path

from . import views_joao as views

app_name = 'core'
urlpatterns = [
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/novo/', views.cliente_criar, name='cliente_criar'),
    path('veiculos/', views.veiculos, name='veiculos'),
    path('veiculos/novo/', views.veiculo_criar, name='veiculo_criar'),
    path('ordens/', views.ordens, name='ordens'),
    path('ordens/<int:pk>/', views.ordem_detalhe, name='ordem_detalhe'),
    path('ordens/<int:pk>/desconto/', views.ordem_desconto, name='ordem_desconto'),
    path('ordens/<int:pk>/pecas/adicionar/', views.ordem_item_adicionar, {'tipo': 'peca'}, name='ordem_peca_adicionar'),
    path('ordens/<int:pk>/servicos/adicionar/', views.ordem_item_adicionar, {'tipo': 'servico'}, name='ordem_servico_adicionar'),
    path('ordens/<int:pk>/pecas/<int:item_id>/remover/', views.ordem_item_remover, {'tipo': 'peca'}, name='ordem_peca_remover'),
    path('ordens/<int:pk>/servicos/<int:item_id>/remover/', views.ordem_item_remover, {'tipo': 'servico'}, name='ordem_servico_remover'),
]
