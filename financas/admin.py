from django.contrib import admin
from .models import Pessoa, Categoria, FormaPagamento, Mes, Receita, Gasto


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome',)


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)


@admin.register(Mes)
class MesAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ano', 'mes')
    list_filter = ('ano',)
    ordering = ('-ano', '-mes')


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'pessoa', 'mes')
    list_filter = ('mes', 'pessoa')
    search_fields = ('descricao',)
    date_hierarchy = 'data'


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'categoria', 'pessoa', 'forma_pagamento', 'mes')
    list_filter = ('mes', 'categoria', 'pessoa', 'forma_pagamento')
    search_fields = ('descricao',)
    date_hierarchy = 'data'