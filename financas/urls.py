from django.urls import path
from . import views

urlpatterns = [
    path('pessoas/', views.pessoa_lista, name='pessoa_lista'),
    path('pessoas/criar/', views.pessoa_criar, name='pessoa_criar'),

    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/criar/', views.categoria_criar, name='categoria_criar'),

    path('formas-pagamento/', views.formapagamento_lista, name='formapagamento_lista'),
    path('formas-pagamento/criar/', views.formapagamento_criar, name='formapagamento_criar'),

    path('meses/', views.mes_lista, name='mes_lista'),
    path('meses/criar/', views.mes_criar, name='mes_criar'),
    path('meses/<int:mes_id>/selecionar/', views.mes_selecionar, name='mes_selecionar'),
    path('receitas/', views.receita_lista, name='receita_lista'),
    path('receitas/criar/', views.receita_criar, name='receita_criar'),    
    path('gastos/', views.gasto_lista, name='gasto_lista'),
    path('gastos/criar/', views.gasto_criar, name='gasto_criar'), 
    path('', views.dashboard, name='dashboard'),
    path('categorias/<int:categoria_id>/excluir/', views.categoria_excluir, name='categoria_excluir'),
    path('categorias/<int:categoria_id>/editar/', views.categoria_editar, name='categoria_editar'),
    path('receitas/<int:receita_id>/editar/', views.receita_editar, name='receita_editar'),
    path('receitas/<int:receita_id>/excluir/', views.receita_excluir, name='receita_excluir'),

    path('gastos/<int:gasto_id>/editar/', views.gasto_editar, name='gasto_editar'),
    path('gastos/<int:gasto_id>/excluir/', views.gasto_excluir, name='gasto_excluir'),
    path('importar-fatura/', views.importar_fatura, name='importar_fatura'),
        path('cartoes/', views.cartao_lista, name='cartao_lista'),
    path('cartoes/criar/', views.cartao_criar, name='cartao_criar'),
    path('cartoes/<int:cartao_id>/editar/', views.cartao_editar, name='cartao_editar'),
    path('cartoes/<int:cartao_id>/excluir/', views.cartao_excluir, name='cartao_excluir'),
    path('projecao/', views.projecao, name='projecao'),
    path('meses/<int:mes_id>/fechar/', views.mes_fechar, name='mes_fechar'),
    path('historico/', views.historico_lista, name='historico_lista'),
    path('historico/<int:mes_id>/', views.historico_detalhe, name='historico_detalhe'),
        path('cofre/', views.cofre, name='cofre'),
    path('cofre/divida/<int:divida_id>/excluir/', views.divida_excluir, name='divida_excluir'), 
        path('meses/<int:mes_id>/clonar/', views.mes_clonar, name='mes_clonar'),
            path('meses/<int:mes_id>/reabrir/', views.mes_reabrir, name='mes_reabrir'),
]