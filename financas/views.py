
import pdfplumber
import re
import json
from datetime import datetime, date
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db import models
from .models import (Pessoa, Categoria, FormaPagamento, Mes, Receita, Gasto, Cartao, Divida, ReservaEmergencia)
from .forms import (PessoaForm, CategoriaForm, FormaPagamentoForm, MesForm, ReceitaForm, GastoForm, CartaoForm, DividaForm, ReservaForm)
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from django.http import HttpResponse
import openpyxl
from openpyxl.chart import PieChart, BarChart, Reference
from openpyxl.utils import get_column_letter
 
# ==========================================
# PESSOAS
# ==========================================
@login_required
def pessoa_lista(request):
    pessoas = Pessoa.objects.all()
    form = PessoaForm()
    return render(request, 'financas/pessoa_lista.html', {'pessoas': pessoas, 'form': form})

@login_required
def pessoa_criar(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pessoa_lista')
    else:
        form = PessoaForm()
    return render(request, 'financas/pessoa_lista.html', {
        'pessoas': Pessoa.objects.all(),
        'form': form,
    })

# ==========================================
# CATEGORIAS
# ==========================================
@login_required
def categoria_lista(request):
    categorias = Categoria.objects.all()
    form = CategoriaForm()
    return render(request, 'financas/categoria_lista.html', {'categorias': categorias, 'form': form})

@login_required
def categoria_criar(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    return render(request, 'financas/categoria_lista.html', {
        'categorias': Categoria.objects.all(),
        'form': form,
    })

@login_required
def categoria_editar(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'financas/categoria_form.html', {'form': form, 'categoria': categoria})

@login_required
def categoria_excluir(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    if request.method == 'POST':
        try:
            nome = categoria.nome
            categoria.delete()
            messages.success(request, f'Categoria "{nome}" excluída com sucesso!')
        except Exception:
            messages.error(request, f'Não é possível excluir "{categoria.nome}" — ela tem gastos vinculados.')
    return redirect('categoria_lista')

# ==========================================
# FORMAS DE PAGAMENTO
# ==========================================
@login_required
def formapagamento_lista(request):
    formas = FormaPagamento.objects.all()
    form = FormaPagamentoForm()
    return render(request, 'financas/formapagamento_lista.html', {'formas': formas, 'form': form})

@login_required
def formapagamento_criar(request):
    if request.method == 'POST':
        form = FormaPagamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('formapagamento_lista')
    else:
        form = FormaPagamentoForm()
    return render(request, 'financas/formapagamento_lista.html', {
        'formas': FormaPagamento.objects.all(),
        'form': form,
    })

# ==========================================
# MESES
# ==========================================
@login_required
def mes_lista(request):
    meses_abertos = Mes.objects.filter(fechado=False).order_by('-ano', '-mes')
    meses_fechados = Mes.objects.filter(fechado=True).order_by('-ano', '-mes')
    form = MesForm()
    mes_ativo_id = request.session.get('mes_ativo_id')
    
    return render(request, 'financas/mes_lista.html', {
        'meses': meses_abertos,
        'meses_fechados': meses_fechados,
        'form': form,
        'mes_ativo_id': mes_ativo_id,
    })

@login_required
def mes_criar(request):
    if request.method == 'POST':
        form = MesForm(request.POST)
        if form.is_valid():
            novo_mes = form.save(commit=False)
            
            # Descobre qual seria o mês anterior lógico (ex: se cria Novembro, o anterior é Outubro)
            data_novo = date(novo_mes.ano, novo_mes.mes, 1)
            data_anterior = data_novo - relativedelta(months=1)
            
            # Tenta achar exatamente o mês anterior
            mes_anterior = Mes.objects.filter(ano=data_anterior.year, mes=data_anterior.month).first()
            
            # Se não achou o mês anterior, busca o último mês que tenha receita (fallback)
            if not mes_anterior:
                mes_anterior = Mes.objects.filter(receitas__isnull=False).order_by('-ano', '-mes').first()
            
            novo_mes.save() # Salva o mês novo primeiro
            
            # Se encontrou um mês para copiar, faz a cópia
            if mes_anterior:
                receitas_antigas = Receita.objects.filter(mes=mes_anterior)
                
                if receitas_antigas.exists():
                    for r in receitas_antigas:
                        Receita.objects.create(
                            mes=novo_mes,
                            descricao=r.descricao,
                            valor=r.valor,
                            data=date(novo_mes.ano, novo_mes.mes, 1),
                            pessoa=r.pessoa
                        )
                    messages.success(request, f'Mês {novo_mes} criado e {receitas_antigas.count()} receitas copiadas de {mes_anterior}!')
                else:
                    messages.warning(request, f'Mês {novo_mes} criado, mas o mês anterior ({mes_anterior}) não tinha receitas para copiar.')
            else:
                messages.success(request, f'Mês {novo_mes} criado! Nenhum mês anterior com receitas foi encontrado.')
                
            return redirect('mes_lista')
    else:
        form = MesForm()
        
    return render(request, 'financas/mes_lista.html', {
        'meses': Mes.objects.filter(fechado=False),
        'meses_fechados': Mes.objects.filter(fechado=True),
        'form': form,
        'mes_ativo_id': request.session.get('mes_ativo_id'),
    })

# @login_required
# def mes_criar(request):
#     if request.method == 'POST':
#         form = MesForm(request.POST)
#         if form.is_valid():
#             novo_mes = form.save(commit=False)
            
#             # Busca o último mês que tem receitas lançadas (para copiar)
#             ultimo_mes_com_receita = Mes.objects.filter(receitas__isnull=False).order_by('-ano', '-mes').first()
            
#             if ultimo_mes_com_receita:
#                 receitas_antigas = Receita.objects.filter(mes=ultimo_mes_com_receita)
#                 novo_mes.save()
                
#                 for r in receitas_antigas:
#                     Receita.objects.create(
#                         mes=novo_mes,
#                         descricao=r.descricao,
#                         valor=r.valor,
#                         data=date(novo_mes.ano, novo_mes.mes, 1),
#                         pessoa=r.pessoa
#                     )
#                 messages.success(request, f'Mês {novo_mes} criado e receitas de {ultimo_mes_com_receita} copiadas!')
#             else:
#                 novo_mes.save()
#                 messages.success(request, f'Mês {novo_mes} criado!')
                
#             return redirect('mes_lista')
#     else:
#         form = MesForm()
        
#     return render(request, 'financas/mes_lista.html', {
#         'meses': Mes.objects.filter(fechado=False),
#         'meses_fechados': Mes.objects.filter(fechado=True),
#         'form': form,
#         'mes_ativo_id': request.session.get('mes_ativo_id'),
#     })

@login_required
def mes_selecionar(request, mes_id):
    if request.method == 'POST':
        request.session['mes_ativo_id'] = mes_id
    return redirect('mes_lista')

@login_required
def mes_fechar(request, mes_id):
    if request.method == 'POST':
        mes_atual = Mes.objects.get(id=mes_id)
        if mes_atual.fechado:
            return redirect('mes_lista')

        mes_atual.fechado = True
        mes_atual.save()

        data_atual = date(mes_atual.ano, mes_atual.mes, 1)
        data_proximo = data_atual + relativedelta(months=1)

        proximo_mes, criado = Mes.objects.get_or_create(
            ano=data_proximo.year,
            mes=data_proximo.month,
            defaults={'fechado': False}
        )

        if criado:
            receitas_antigas = Receita.objects.filter(mes=mes_atual)
            for r in receitas_antigas:
                Receita.objects.create(
                    mes=proximo_mes,
                    descricao=r.descricao,
                    valor=r.valor,
                    data=data_proximo,
                    pessoa=r.pessoa
                )
            messages.success(request, f'Mês {mes_atual} fechado! As receitas foram copiadas para {proximo_mes}.')
        else:
            messages.success(request, f'Mês {mes_atual} fechado! O mês {proximo_mes} já estava aberto.')

        request.session['mes_ativo_id'] = proximo_mes.id

    return redirect('mes_lista')

@login_required
def mes_reabrir(request, mes_id):
    if request.method == 'POST':
        mes = Mes.objects.get(id=mes_id)
        mes.fechado = False
        mes.save()
        messages.success(request, f'Mês {mes} reaberto com sucesso!')
    return redirect('mes_lista')

@login_required
def mes_clonar(request, mes_id):
    if request.method == 'POST':
        mes_atual = Mes.objects.get(id=mes_id)
        data_atual = date(mes_atual.ano, mes_atual.mes, 1)
        data_anterior = data_atual - relativedelta(months=1)
        
        mes_anterior = Mes.objects.filter(ano=data_anterior.year, mes=data_anterior.month).first()
        
        if not mes_anterior:
            messages.error(request, 'Não encontrei o mês anterior para clonar.')
            return redirect('mes_lista')

        # Copia Receitas
        receitas_antigas = Receita.objects.filter(mes=mes_anterior)
        for r in receitas_antigas:
            Receita.objects.create(
                mes=mes_atual,
                descricao=r.descricao,
                valor=r.valor,
                data=date(mes_atual.ano, mes_atual.mes, 1),
                pessoa=r.pessoa
            )

        # Copia Gastos (sem cartão)
        gastos_antigos = Gasto.objects.filter(mes=mes_anterior, cartao__isnull=True)
        for g in gastos_antigos:
            Gasto.objects.create(
                mes=mes_atual,
                descricao=g.descricao,
                valor=g.valor,
                data=date(mes_atual.ano, mes_atual.mes, 1),
                categoria=g.categoria,
                pessoa=g.pessoa,
                forma_pagamento=g.forma_pagamento,
                cartao=None
            )

        messages.success(request, f'Mês clonado com sucesso a partir de {mes_anterior}!')
        return redirect('mes_lista')

    return redirect('mes_lista')

# ==========================================
# RECEITAS
# ==========================================
@login_required
def receita_lista(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return render(request, 'financas/receita_lista.html', {
            'sem_mes_ativo': True,
            'receitas': [],
            'form': None,
        })

    mes_ativo = Mes.objects.get(id=mes_ativo_id)
    receitas = Receita.objects.filter(mes=mes_ativo)
    form = ReceitaForm()
    total = sum(r.valor for r in receitas)

    return render(request, 'financas/receita_lista.html', {
        'sem_mes_ativo': False,
        'mes_ativo': mes_ativo,
        'receitas': receitas,
        'form': form,
        'total': total,
    })

@login_required
def receita_criar(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return redirect('mes_lista')

    if request.method == 'POST':
        form = ReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.mes = Mes.objects.get(id=mes_ativo_id)
            receita.save()
            return redirect('receita_lista')
    else:
        form = ReceitaForm()

    return render(request, 'financas/receita_lista.html', {
        'sem_mes_ativo': False,
        'mes_ativo': Mes.objects.get(id=mes_ativo_id),
        'receitas': Receita.objects.filter(mes_id=mes_ativo_id),
        'form': form,
        'total': sum(r.valor for r in Receita.objects.filter(mes_id=mes_ativo_id)),
    })

@login_required
def receita_excluir(request, receita_id):
    receita = Receita.objects.get(id=receita_id)
    if request.method == 'POST':
        receita.delete()
        messages.success(request, 'Receita excluída com sucesso!')
    return redirect('receita_lista')

@login_required
def receita_editar(request, receita_id):
    receita = Receita.objects.get(id=receita_id)
    if request.method == 'POST':
        form = ReceitaForm(request.POST, instance=receita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receita atualizada com sucesso!')
            return redirect('receita_lista')
    else:
        form = ReceitaForm(instance=receita)
    return render(request, 'financas/receita_form.html', {'form': form, 'receita': receita})

# ==========================================
# GASTOS
# ==========================================
@login_required
def gasto_lista(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return render(request, 'financas/gasto_lista.html', {
            'sem_mes_ativo': True,
            'gastos': [],
            'form': None,
        })

    mes_ativo = Mes.objects.get(id=mes_ativo_id)
    gastos = Gasto.objects.filter(mes=mes_ativo)
    form = GastoForm()
    total = sum(g.valor for g in gastos)

    return render(request, 'financas/gasto_lista.html', {
        'sem_mes_ativo': False,
        'mes_ativo': mes_ativo,
        'gastos': gastos,
        'form': form,
        'total': total,
    })

@login_required
def gasto_criar(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return redirect('mes_lista')

    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto_base = form.save(commit=False)
            mes_ativo = Mes.objects.get(id=mes_ativo_id)
            
            parcela_atual = form.cleaned_data.get('parcela_atual') or 1
            total_parcelas = form.cleaned_data.get('total_parcelas') or 1
            
            # Se o cara digitou a parcela atual maior que o total, corrige
            if parcela_atual > total_parcelas:
                parcela_atual = total_parcelas
                
            valor_total = gasto_base.valor
            
            if total_parcelas > 1:
                # Valor de cada parcela
                valor_parcela = round(valor_total / total_parcelas, 2)
                data_base = gasto_base.data
                
                # Loop para criar todas as parcelas (do número atual até o total)
                for i in range(parcela_atual, total_parcelas + 1):
                    # Avança a data a partir de HOJE (a parcela atual é lançada no mês ativo)
                    meses_a_avancar = i - parcela_atual
                    nova_data = data_base + relativedelta(months=meses_a_avancar)
                    
                    # Descobre o mês da parcela
                    if i == parcela_atual:
                        mes_parcela = mes_ativo
                    else:
                        mes_parcela, _ = Mes.objects.get_or_create(ano=nova_data.year, mes=nova_data.month)
                    
                    Gasto.objects.create(
                        mes=mes_parcela,
                        descricao=f"{gasto_base.descricao} ({i}/{total_parcelas})",
                        valor=valor_parcela,
                        data=nova_data,
                        categoria=gasto_base.categoria,
                        pessoa=gasto_base.pessoa,
                        forma_pagamento=gasto_base.forma_pagamento,
                        cartao=gasto_base.cartao
                    )
                messages.success(request, f'Gasto parcelado lançado! Parcelas {parcela_atual}/{total_parcelas} até {total_parcelas}/{total_parcelas}.')
            else:
                # Se for 1 única parcela, salva normal
                gasto_base.mes = mes_ativo
                gasto_base.save()
                messages.success(request, 'Gasto lançado com sucesso!')
                
            return redirect('gasto_lista')
    else:
        form = GastoForm()

    mes_ativo = Mes.objects.get(id=mes_ativo_id)
    gastos = Gasto.objects.filter(mes=mes_ativo)

    return render(request, 'financas/gasto_lista.html', {
        'sem_mes_ativo': False,
        'mes_ativo': mes_ativo,
        'gastos': gastos,
        'form': form,
        'total': sum(g.valor for g in gastos),
    })

# @login_required
# def gasto_criar(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return redirect('mes_lista')

#     if request.method == 'POST':
#         form = GastoForm(request.POST)
#         if form.is_valid():
#             # Pega os dados do formulário
#             gasto_base = form.save(commit=False)
#             gasto_base.mes = Mes.objects.get(id=mes_ativo_id)
            
#             # Lê a quantidade de parcelas (se não preencher, é 1)
#             parcelas = form.cleaned_data.get('parcelas') or 1
#             valor_total = gasto_base.valor
            
#             if parcelas > 1:
#                 # Divide o valor total pelo número de parcelas
#                 valor_parcela = valor_total / parcelas
#                 # Arredonda pra 2 casas decimais (Ex: 3333.33)
#                 valor_parcela = round(valor_parcela, 2)
                
#                 data_base = gasto_base.data
                
#                 for i in range(parcelas):
#                     # 1. Cria uma cópia do objeto base
#                     novo_gasto = Gasto.objects.create(
#                         mes=gasto_base.mes, # Vamos atualizar isso abaixo
#                         descricao=f"{gasto_base.descricao} ({i+1}/{parcelas})",
#                         valor=valor_parcela,
#                         data=data_base,
#                         categoria=gasto_base.categoria,
#                         pessoa=gasto_base.pessoa,
#                         forma_pagamento=gasto_base.forma_pagamento,
#                         cartao=gasto_base.cartao
#                     )
                    
#                     # 2. Joga a data e o mês para frente (se for a partir da 2ª parcela)
#                     if i > 0:
#                         nova_data = data_base + relativedelta(months=i)
#                         novo_mes, _ = Mes.objects.get_or_create(ano=nova_data.year, mes=nova_data.month)
#                         novo_gasto.data = nova_data
#                         novo_gasto.mes = novo_mes
#                         novo_gasto.save()
                        
#             else:
#                 # Se for só 1 parcela, salva normal
#                 gasto_base.save()
                
#             messages.success(request, 'Gasto lançado com sucesso!')
#             return redirect('gasto_lista')
#     else:
#         form = GastoForm()

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
#     gastos = Gasto.objects.filter(mes=mes_ativo)

#     return render(request, 'financas/gasto_lista.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'gastos': gastos,
#         'form': form,
#         'total': sum(g.valor for g in gastos),
#     })

# @login_required
# def gasto_criar(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return redirect('mes_lista')

#     if request.method == 'POST':
#         form = GastoForm(request.POST)
#         if form.is_valid():
#             gasto = form.save(commit=False)
#             gasto.mes = Mes.objects.get(id=mes_ativo_id)
#             gasto.save()
#             return redirect('gasto_lista')
#     else:
#         form = GastoForm()

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
#     gastos = Gasto.objects.filter(mes=mes_ativo)

#     return render(request, 'financas/gasto_lista.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'gastos': gastos,
#         'form': form,
#         'total': sum(g.valor for g in gastos),
#     })

@login_required
def gasto_excluir(request, gasto_id):
    gasto = Gasto.objects.get(id=gasto_id)
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, 'Gasto excluído com sucesso!')
    return redirect('gasto_lista')

@login_required
def gasto_editar(request, gasto_id):
    gasto = Gasto.objects.get(id=gasto_id)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto atualizado com sucesso!')
            return redirect('gasto_lista')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'financas/gasto_form.html', {'form': form, 'gasto': gasto})

# ==========================================
# CARTÕES
# ==========================================
@login_required
def cartao_lista(request):
    cartoes = Cartao.objects.all()
    form = CartaoForm()
    return render(request, 'financas/cartao_lista.html', {'cartoes': cartoes, 'form': form})

@login_required
def cartao_criar(request):
    if request.method == 'POST':
        form = CartaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cartão cadastrado com sucesso!')
            return redirect('cartao_lista')
    else:
        form = CartaoForm()
    return render(request, 'financas/cartao_lista.html', {
        'cartoes': Cartao.objects.all(),
        'form': form,
    })

@login_required
def cartao_editar(request, cartao_id):
    cartao = Cartao.objects.get(id=cartao_id)
    if request.method == 'POST':
        form = CartaoForm(request.POST, instance=cartao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cartão atualizado com sucesso!')
            return redirect('cartao_lista')
    else:
        form = CartaoForm(instance=cartao)
    return render(request, 'financas/cartao_form.html', {'form': form, 'cartao': cartao})

@login_required
def cartao_excluir(request, cartao_id):
    cartao = Cartao.objects.get(id=cartao_id)
    if request.method == 'POST':
        try:
            nome = cartao.nome
            cartao.delete()
            messages.success(request, f'Cartão "{nome}" excluído com sucesso!')
        except Exception:
            messages.error(request, f'Não é possível excluir "{cartao.nome}" — ele tem gastos vinculados.')
    return redirect('cartao_lista')

# ==========================================
# DASHBOARD
# ==========================================
@login_required
def dashboard(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return render(request, 'financas/dashboard.html', {'sem_mes_ativo': True})

    mes_ativo = Mes.objects.get(id=mes_ativo_id)

    # Totais
    total_receitas = Receita.objects.filter(mes=mes_ativo).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    total_gastos = Gasto.objects.filter(mes=mes_ativo).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    verba = total_receitas - total_gastos

    # Alerta
    if total_receitas == 0:
        alerta = 'sem_receita'
    elif verba < 0:
        alerta = 'estourado'
    elif verba < (total_receitas * Decimal('0.10')):
        alerta = 'apertado'
    else:
        alerta = 'ok'

    # 50-30-20
    gastos_essenciais = Gasto.objects.filter(
        mes=mes_ativo, categoria__tipo='E'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    gastos_nao_essenciais = Gasto.objects.filter(
        mes=mes_ativo, categoria__tipo='N'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    if total_receitas > 0:
        pct_essenciais = float((gastos_essenciais / total_receitas) * 100)
        pct_nao_essenciais = float((gastos_nao_essenciais / total_receitas) * 100)
        pct_sobra = float((verba / total_receitas) * 100)
    else:
        pct_essenciais = 0
        pct_nao_essenciais = 0
        pct_sobra = 0

    # Orçamentos por categoria
    categorias_com_limite = Categoria.objects.filter(
        ativo=True, limite_mensal__isnull=False
    ).exclude(limite_mensal=0)

    orcamentos = []
    for cat in categorias_com_limite:
        gasto_cat = Gasto.objects.filter(
            mes=mes_ativo, categoria=cat
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

        pct_usado = float((gasto_cat / cat.limite_mensal) * 100) if cat.limite_mensal > 0 else 0
        restante = cat.limite_mensal - gasto_cat

        if pct_usado > 100:
            cor = 'danger'
        elif pct_usado >= 70:
            cor = 'warning'
        else:
            cor = 'success'

        orcamentos.append({
            'categoria': cat,
            'gasto': gasto_cat,
            'limite': cat.limite_mensal,
            'restante': restante,
            'pct_usado': pct_usado,
            'cor': cor,
        })

    # --- CARTÕES ---
    cartoes_ativos = Cartao.objects.filter(ativo=True)
    resumo_cartoes = []
    
    for c in cartoes_ativos:
        total_cartao = Gasto.objects.filter(
            mes=mes_ativo, cartao=c
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        resumo_cartoes.append({
            'cartao': c,
            'total_mes': total_cartao
        })

    # Últimos 5 lançamentos
    ultimas_receitas = Receita.objects.filter(mes=mes_ativo).order_by('-id')[:5]
    ultimos_gastos = Gasto.objects.filter(mes=mes_ativo).order_by('-id')[:5]

    # --- DADOS PARA O GRÁFICO (GASTOS POR CATEGORIA) ---
    gastos_por_categoria = Gasto.objects.filter(mes=mes_ativo).values('categoria__nome').annotate(
        total=Sum('valor')
    ).order_by('-total')

    grafico_labels = [item['categoria__nome'] for item in gastos_por_categoria]
    grafico_valores = [float(item['total']) for item in gastos_por_categoria]

    return render(request, 'financas/dashboard.html', {
        'sem_mes_ativo': False,
        'mes_ativo': mes_ativo,
        'total_receitas': total_receitas,
        'total_gastos': total_gastos,
        'verba': verba,
        'alerta': alerta,
        'gastos_essenciais': gastos_essenciais,
        'gastos_nao_essenciais': gastos_nao_essenciais,
        'pct_essenciais': pct_essenciais,
        'pct_nao_essenciais': pct_nao_essenciais,
        'pct_sobra': pct_sobra,
        'orcamentos': orcamentos,
        'resumo_cartoes': resumo_cartoes,
        'ultimas_receitas': ultimas_receitas,
        'ultimos_gastos': ultimos_gastos,
        'grafico_labels': grafico_labels,
        'grafico_valores': grafico_valores,
    })

# ==========================================
# IMPORTAÇÃO DE FATURA
# ==========================================
# IMPORTAÇÃO DE FATURA
# ==========================================

@login_required
def importar_fatura(request):
    # 1. SE FOR POST E TIVER DADOS DE CONFIRMAÇÃO (Salvar no banco)
    if request.method == 'POST' and 'salvar_importacao' in request.POST:
        mes_ativo_id = request.session.get('mes_ativo_id')
        if not mes_ativo_id:
            messages.error(request, 'Nenhum mês ativo selecionado.')
            return redirect('mes_lista')

        mes_ativo = Mes.objects.get(id=mes_ativo_id)
        categoria_id = request.POST.get('categoria')
        pessoa_id = request.POST.get('pessoa')
        cartao_id = request.POST.get('cartao')
        
        datas = request.POST.getlist('data[]')
        descricoes = request.POST.getlist('descricao[]')
        valores = request.POST.getlist('valor[]')

        if not (categoria_id and pessoa_id and cartao_id and datas):
            messages.error(request, 'Preencha todos os campos e selecione pelo menos um gasto.')
            return redirect('importar_fatura')

        categoria = Categoria.objects.get(id=categoria_id)
        pessoa = Pessoa.objects.get(id=pessoa_id)
        cartao = Cartao.objects.get(id=cartao_id)
        
        forma_credito, _ = FormaPagamento.objects.get_or_create(nome="Cartão de Crédito")
        salvos = 0
        
        for i in range(len(datas)):
            descricao_original = descricoes[i]
            descricao_limpa = re.sub(r'^[•\s\d]+', '', descricao_original).strip()
            
            valor = Decimal(str(valores[i]))
            data_gasto = datetime.strptime(datas[i], '%Y-%m-%d').date()
            
            match_parcela = re.search(r'Parcela (\d+)/(\d+)', descricao_limpa)
            
            if match_parcela:
                parcela_atual = int(match_parcela.group(1))
                total_parcelas = int(match_parcela.group(2))
                parcelas_restantes = total_parcelas - parcela_atual
                
                Gasto.objects.create(
                    mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
                    categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
                )
                
                for j in range(1, parcelas_restantes + 1):
                    nova_data = data_gasto + relativedelta(months=j)
                    mes_futuro = mes_ativo.mes + j
                    ano_futuro = mes_ativo.ano
                    if mes_futuro > 12:
                        mes_futuro -= 12
                        ano_futuro += 1
                        
                    novo_mes, _ = Mes.objects.get_or_create(ano=ano_futuro, mes=mes_futuro)
                    nova_descricao = re.sub(r'Parcela \d+/\d+', f'Parcela {parcela_atual + j}/{total_parcelas}', descricao_limpa)
                    
                    Gasto.objects.create(
                        mes=novo_mes, descricao=nova_descricao, valor=valor, data=nova_data,
                        categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
                    )
            else:
                Gasto.objects.create(
                    mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
                    categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
                )
            salvos += 1
            
        messages.success(request, f'{salvos} transações importadas com sucesso!')
        return redirect('gasto_lista')

    # 2. SE FOR POST (Ler o PDF)
    if request.method == 'POST' and request.FILES.get('arquivo_pdf'):
        mes_ativo_id = request.session.get('mes_ativo_id')
        if not mes_ativo_id:
            messages.error(request, 'Nenhum mês ativo selecionado.')
            return redirect('mes_lista')
        mes_ativo = Mes.objects.get(id=mes_ativo_id)

        pdf_file = request.FILES.get('arquivo_pdf')
        transacoes = []
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if not texto:
                        continue
                        
                    linhas = texto.split('\n')
                    for linha in linhas:
                        # Regex CIRÚRGICO:
                        # 1. Procura no início da linha a data (ex: 26 SET)
                        # 2. Permite que existam 4 a 6 números (ex: 9970) e os pula
                        # 3. Captura o nome (que pode ter espaços)
                        # 4. Exige o R$ e o valor com vírgula e duas casas decimais no final.
                        match = re.match(r'^(\d{2}\s[A-Z]{3})\s*(?:\d{4,6})?\s*(.*?)\s*R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})', linha)
                        
                        if match:
                            data_str = match.group(1)
                            descricao = match.group(2).strip()
                            valor_str = match.group(3)
                            
                            # Ignora lixos
                            # Ignora APENAS as linhas de pagamento de fatura e totais
                            if descricao.startswith("Pagamento em") or "Total a pagar" in descricao or "Fatura anterior" in descricao:
                                continue
                            
                            valor_limpo = valor_str.replace('.', '').replace(',', '.')
                            valor = Decimal(valor_limpo)
                            
                            meses = {'JAN':1, 'FEV':2, 'MAR':3, 'ABR':4, 'MAI':5, 'JUN':6, 
                                     'JUL':7, 'AGO':8, 'SET':9, 'OUT':10, 'NOV':11, 'DEZ':12}
                            dia, mes_abrev = data_str.split()
                            mes = meses.get(mes_abrev, 1)
                            ano = datetime.now().year
                            
                            # Se a compra foi em um mês maior que a fatura, foi no ano passado
                            if mes > mes_ativo.mes:
                                ano = ano - 1
                                
                            data_gasto = date(ano, mes, int(dia))
                            
                            # Limpa sujeira
                            descricao_limpa = re.sub(r'^[•\s\d]+', '', descricao).strip()
                            
                            transacoes.append({
                                'data': data_gasto.isoformat(),
                                'descricao': descricao_limpa,
                                'valor': str(valor)
                            })
        except Exception as e:
            messages.error(request, f'Erro ao ler PDF: {e}')
            return redirect('importar_fatura')

        if not transacoes:
            messages.warning(request, 'Nenhuma transação válida encontrada no PDF.')

        categorias = Categoria.objects.filter(ativo=True)
        pessoas = Pessoa.objects.filter(ativo=True)
        cartoes = Cartao.objects.filter(ativo=True)

        return render(request, 'financas/importar_fatura.html', {
            'transacoes': transacoes,
            'total': sum(Decimal(t['valor']) for t in transacoes),
            'categorias': categorias,
            'pessoas': pessoas,
            'cartoes': cartoes,
        })

    return render(request, 'financas/importar_fatura.html')
# @login_required
# def importar_fatura(request):
#     if request.method == 'POST' and 'salvar_importacao' in request.POST:
#         mes_ativo_id = request.session.get('mes_ativo_id')
#         if not mes_ativo_id:
#             messages.error(request, 'Nenhum mês ativo selecionado.')
#             return redirect('mes_lista')

#         mes_ativo = Mes.objects.get(id=mes_ativo_id)
#         categoria_id = request.POST.get('categoria')
#         pessoa_id = request.POST.get('pessoa')
#         cartao_id = request.POST.get('cartao')
        
#         datas = request.POST.getlist('data[]')
#         descricoes = request.POST.getlist('descricao[]')
#         valores = request.POST.getlist('valor[]')

#         if not (categoria_id and pessoa_id and cartao_id and datas):
#             messages.error(request, 'Preencha todos os campos e selecione pelo menos um gasto.')
#             return redirect('importar_fatura')

#         categoria = Categoria.objects.get(id=categoria_id)
#         pessoa = Pessoa.objects.get(id=pessoa_id)
#         cartao = Cartao.objects.get(id=cartao_id)
        
#         forma_credito, _ = FormaPagamento.objects.get_or_create(nome="Cartão de Crédito")
#         salvos = 0
        
#         for i in range(len(datas)):
#             descricao_original = descricoes[i]
#             descricao_limpa = re.sub(r'^[•\s\d]+', '', descricao_original).strip()
            
#             valor = Decimal(str(valores[i]))
#             data_gasto = datetime.strptime(datas[i], '%Y-%m-%d').date()
            
#             match_parcela = re.search(r'Parcela (\d+)/(\d+)', descricao_limpa)
            
#             if match_parcela:
#                 parcela_atual = int(match_parcela.group(1))
#                 total_parcelas = int(match_parcela.group(2))
#                 parcelas_restantes = total_parcelas - parcela_atual
                
#                 Gasto.objects.create(
#                     mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
#                     categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                 )
                
#                 for j in range(1, parcelas_restantes + 1):
#                     nova_data = data_gasto + relativedelta(months=j)
#                     mes_futuro = mes_ativo.mes + j
#                     ano_futuro = mes_ativo.ano
#                     if mes_futuro > 12:
#                         mes_futuro -= 12
#                         ano_futuro += 1
                        
#                     novo_mes, _ = Mes.objects.get_or_create(ano=ano_futuro, mes=mes_futuro)
#                     nova_descricao = re.sub(r'Parcela \d+/\d+', f'Parcela {parcela_atual + j}/{total_parcelas}', descricao_limpa)
                    
#                     Gasto.objects.create(
#                         mes=novo_mes, descricao=nova_descricao, valor=valor, data=nova_data,
#                         categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                     )
#             else:
#                 Gasto.objects.create(
#                     mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
#                     categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                 )
#             salvos += 1
            
#         messages.success(request, f'{salvos} transações importadas com sucesso!')
#         return redirect('gasto_lista')

#     if request.method == 'POST' and request.FILES.get('arquivo_pdf'):
#         pdf_file = request.FILES.get('arquivo_pdf')
#         transacoes = []
        
#         try:
#             with pdfplumber.open(pdf_file) as pdf:
#                 for page in pdf.pages:
#                     texto = page.extract_text()
#                     if not texto or ("TRANSACÕES" not in texto and "TRANSAÇÕES" not in texto):
#                         continue
                        
#                     linhas = texto.split('\n')
#                     for linha in linhas:
#                         # MÁGICA AQUI: O Regex ignora os números estranhos (9970, 0230) entre a data e o nome
#                         match = re.match(r'^(\d{2}\s[A-Z]{3})\s*(?:\d{4,6})?\s*(.*?)\s+R\$\s*([\d\.]+,\d{2})', linha)
                        
#                         if match:
#                             data_str = match.group(1)
#                             descricao = match.group(2).strip()
#                             valor_str = match.group(3)
                            
#                             # Ignora a linha de pagamento
#                             if "Pagamento" in descricao:
#                                 continue
                            
#                             valor_limpo = valor_str.replace('.', '').replace(',', '.')
#                             valor = Decimal(valor_limpo)
                            
#                             meses = {'JAN':1, 'FEV':2, 'MAR':3, 'ABR':4, 'MAI':5, 'JUN':6, 'JUL':7, 'AGO':8, 'SET':9, 'OUT':10, 'NOV':11, 'DEZ':12}
#                             dia, mes_abrev = data_str.split()
#                             mes = meses.get(mes_abrev, 1)
#                             ano = datetime.now().year
#                             data_gasto = date(ano, mes, int(dia))
                            
#                             # Limpa qualquer sujeira que tenha sobrado no começo da descrição
#                             descricao_limpa = re.sub(r'^[•\s\d]+', '', descricao).strip()
                            
#                             transacoes.append({
#                                 'data': data_gasto.isoformat(),
#                                 'descricao': descricao_limpa,
#                                 'valor': str(valor)
#                             })
#         except Exception as e:
#             messages.error(request, f'Erro ao ler PDF: {e}')
#             return redirect('importar_fatura')

#         if not transacoes:
#             messages.warning(request, 'Nenhuma transação válida encontrada no PDF.')

#         categorias = Categoria.objects.filter(ativo=True)
#         pessoas = Pessoa.objects.filter(ativo=True)
#         cartoes = Cartao.objects.filter(ativo=True)

#         return render(request, 'financas/importar_fatura.html', {
#             'transacoes': transacoes,
#             'total': sum(Decimal(t['valor']) for t in transacoes),
#             'categorias': categorias,
#             'pessoas': pessoas,
#             'cartoes': cartoes,
#         })

#     return render(request, 'financas/importar_fatura.html')

# ==========================================
# @login_required
# def importar_fatura(request):
#     if request.method == 'POST' and 'salvar_importacao' in request.POST:
#         mes_ativo_id = request.session.get('mes_ativo_id')
#         if not mes_ativo_id:
#             messages.error(request, 'Nenhum mês ativo selecionado.')
#             return redirect('mes_lista')

#         mes_ativo = Mes.objects.get(id=mes_ativo_id)
#         categoria_id = request.POST.get('categoria')
#         pessoa_id = request.POST.get('pessoa')
#         cartao_id = request.POST.get('cartao')
        
#         datas = request.POST.getlist('data[]')
#         descricoes = request.POST.getlist('descricao[]')
#         valores = request.POST.getlist('valor[]')

#         if not (categoria_id and pessoa_id and cartao_id and datas):
#             messages.error(request, 'Preencha todos os campos e selecione pelo menos um gasto.')
#             return redirect('importar_fatura')

#         categoria = Categoria.objects.get(id=categoria_id)
#         pessoa = Pessoa.objects.get(id=pessoa_id)
#         cartao = Cartao.objects.get(id=cartao_id)
        
#         forma_credito, _ = FormaPagamento.objects.get_or_create(nome="Cartão de Crédito")
#         salvos = 0
        
#         for i in range(len(datas)):
#             descricao_original = descricoes[i]
#             descricao_limpa = re.sub(r'^[•\s\d]+', '', descricao_original).strip()
            
#             valor = Decimal(str(valores[i]))
#             data_gasto = datetime.strptime(datas[i], '%Y-%m-%d').date()
            
#             match_parcela = re.search(r'Parcela (\d+)/(\d+)', descricao_limpa)
            
#             if match_parcela:
#                 parcela_atual = int(match_parcela.group(1))
#                 total_parcelas = int(match_parcela.group(2))
#                 parcelas_restantes = total_parcelas - parcela_atual
                
#                 Gasto.objects.create(
#                     mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
#                     categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                 )
                
#                 for j in range(1, parcelas_restantes + 1):
#                     nova_data = data_gasto + relativedelta(months=j)
#                     mes_futuro = mes_ativo.mes + j
#                     ano_futuro = mes_ativo.ano
#                     if mes_futuro > 12:
#                         mes_futuro -= 12
#                         ano_futuro += 1
                        
#                     novo_mes, _ = Mes.objects.get_or_create(ano=ano_futuro, mes=mes_futuro)
#                     nova_descricao = re.sub(r'Parcela \d+/\d+', f'Parcela {parcela_atual + j}/{total_parcelas}', descricao_limpa)
                    
#                     Gasto.objects.create(
#                         mes=novo_mes, descricao=nova_descricao, valor=valor, data=nova_data,
#                         categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                     )
#             else:
#                 Gasto.objects.create(
#                     mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
#                     categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                 )
#             salvos += 1
            
#         messages.success(request, f'{salvos} transações importadas com sucesso!')
#         return redirect('gasto_lista')

#     if request.method == 'POST' and request.FILES.get('arquivo_pdf'):
#         pdf_file = request.FILES.get('arquivo_pdf')
#         transacoes = []
        
#         try:
#             with pdfplumber.open(pdf_file) as pdf:
#                 for page in pdf.pages:
#                     texto = page.extract_text()
#                     if not texto or ("TRANSACÕES" not in texto and "TRANSAÇÕES" not in texto):
#                         continue
                        
#                     linhas = texto.split('\n')
#                     for linha in linhas:
#                         match = re.match(r'^(\d{2}\s[A-Z]{3})\s+(.*?)\s+R\$\s*([\d\.]+,\d{2})', linha)
#                         if match:
#                             data_str = match.group(1)
#                             descricao = match.group(2).strip()
#                             valor_str = match.group(3)
                            
#                             if "Pagamento" in descricao:
#                                 continue
                            
#                             valor_limpo = valor_str.replace('.', '').replace(',', '.')
#                             valor = Decimal(valor_limpo)
                            
#                             meses = {'JAN':1, 'FEV':2, 'MAR':3, 'ABR':4, 'MAI':5, 'JUN':6, 'JUL':7, 'AGO':8, 'SET':9, 'OUT':10, 'NOV':11, 'DEZ':12}
#                             dia, mes_abrev = data_str.split()
#                             mes = meses.get(mes_abrev, 1)
#                             ano = datetime.now().year
#                             data_gasto = date(ano, mes, int(dia))
                            
#                             transacoes.append({
#                                 'data': data_gasto.isoformat(),
#                                 'descricao': descricao,
#                                 'valor': str(valor)
#                             })
#         except Exception as e:
#             messages.error(request, f'Erro ao ler PDF: {e}')
#             return redirect('importar_fatura')

#         if not transacoes:
#             messages.warning(request, 'Nenhuma transação válida encontrada no PDF.')

#         categorias = Categoria.objects.filter(ativo=True)
#         pessoas = Pessoa.objects.filter(ativo=True)
#         cartoes = Cartao.objects.filter(ativo=True)

#         return render(request, 'financas/importar_fatura.html', {
#             'transacoes': transacoes,
#             'total': sum(Decimal(t['valor']) for t in transacoes),
#             'categorias': categorias,
#             'pessoas': pessoas,
#             'cartoes': cartoes,
#         })

#     return render(request, 'financas/importar_fatura.html')

# ==========================================
# PROJEÇÃO 12 MESES
# ==========================================

@login_required
def projecao(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return render(request, 'financas/projecao.html', {'sem_mes_ativo': True})

    mes_ativo = Mes.objects.get(id=mes_ativo_id)
    
    ano_base = int(request.GET.get('ano', mes_ativo.ano))
    mes_base = int(request.GET.get('mes', mes_ativo.mes))
    
    nomes_meses = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    meses_colunas = []
    data_atual = date(ano_base, mes_base, 1)
    
    for i in range(12):
        mes_alvo = data_atual + relativedelta(months=i)
        meses_colunas.append({
            'id': f"{mes_alvo.year}-{mes_alvo.month}",
            'nome': f"{nomes_meses[mes_alvo.month]}/{mes_alvo.year}", 
            'ano': mes_alvo.year,
            'mes': mes_alvo.month,
        })

    data_anterior = data_atual - relativedelta(months=1)
    data_posterior = data_atual + relativedelta(months=1)
    
    anos_filtro = list(set([m['ano'] for m in meses_colunas]))
    
    gastos_periodo = Gasto.objects.filter(
        mes__ano__in=anos_filtro
    ).select_related('mes', 'cartao')

    agrupado = {}
    totais_colunas = {m['id']: Decimal('0') for m in meses_colunas}

    for g in gastos_periodo:
        id_mes = f"{g.mes.ano}-{g.mes.mes}"
        
        if id_mes not in totais_colunas:
            continue

        # MÁGICA AQUI: Remove o padrão " (1/10)", " - Parcela 1/10" ou " (1/10) " do final do nome
        # O Regex procura qualquer número entre parênteses ou após a palavra "Parcela"
        nome_limpo = re.sub(r'\s*\(\d+/\d+\)|\s*-\s*Parcela\s*\d+/\d+', '', g.descricao).strip()
        
        if not nome_limpo:
            nome_limpo = g.descricao
            
        if nome_limpo not in agrupado:
            agrupado[nome_limpo] = {}
            
        if id_mes not in agrupado[nome_limpo]:
            agrupado[nome_limpo][id_mes] = Decimal('0')
            
        agrupado[nome_limpo][id_mes] += g.valor
        totais_colunas[id_mes] += g.valor

    linhas_projecao = []
    for nome_gasto, valores_meses in agrupado.items():
        linhas_projecao.append({
            'categoria': nome_gasto,
            'valores': valores_meses
        })
        
    linhas_projecao = sorted(linhas_projecao, key=lambda x: x['categoria'].lower())

    return render(request, 'financas/projecao.html', {
        'sem_mes_ativo': False,
        'mes_ativo': mes_ativo,
        'meses_colunas': meses_colunas,
        'linhas_projecao': linhas_projecao,
        'totais_colunas': totais_colunas,
        'ano_base': ano_base,
        'mes_base': mes_base,
        'mes_base_nome': f"{nomes_meses[mes_base]}/{ano_base}",
        'ano_anterior': data_anterior.year,
        'mes_anterior': data_anterior.month,
        'ano_posterior': data_posterior.year,
        'mes_posterior': data_posterior.month,
    })

# @login_required
# def projecao(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return render(request, 'financas/projecao.html', {'sem_mes_ativo': True})

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
    
#     ano_base = int(request.GET.get('ano', mes_ativo.ano))
#     mes_base = int(request.GET.get('mes', mes_ativo.mes))
    
#     nomes_meses = {
#         1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
#         7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
#     }

#     meses_colunas = []
#     data_atual = date(ano_base, mes_base, 1)
    
#     for i in range(12):
#         mes_alvo = data_atual + relativedelta(months=i)
#         meses_colunas.append({
#             'id': f"{mes_alvo.year}-{mes_alvo.month}",
#             'nome': f"{nomes_meses[mes_alvo.month]}/{mes_alvo.year}", 
#             'ano': mes_alvo.year,
#             'mes': mes_alvo.month,
#         })

#     data_anterior = data_atual - relativedelta(months=1)
#     data_posterior = data_atual + relativedelta(months=1)
    
#     anos_filtro = list(set([m['ano'] for m in meses_colunas]))
    
#     gastos_periodo = Gasto.objects.filter(
#         mes__ano__in=anos_filtro
#     ).select_related('mes', 'cartao')

#     agrupado = {}
#     totais_colunas = {m['id']: Decimal('0') for m in meses_colunas}

#     for g in gastos_periodo:
#         id_mes = f"{g.mes.ano}-{g.mes.mes}"
        
#         if id_mes not in totais_colunas:
#             continue

#         nome_limpo = re.sub(r'- Parcela \d+/\d+', '', g.descricao).strip()
#         if not nome_limpo:
#             nome_limpo = g.descricao
            
#         if nome_limpo not in agrupado:
#             agrupado[nome_limpo] = {}
            
#         if id_mes not in agrupado[nome_limpo]:
#             agrupado[nome_limpo][id_mes] = Decimal('0')
            
#         agrupado[nome_limpo][id_mes] += g.valor
#         totais_colunas[id_mes] += g.valor

#     linhas_projecao = []
#     for nome_gasto, valores_meses in agrupado.items():
#         linhas_projecao.append({
#             'categoria': nome_gasto,
#             'valores': valores_meses
#         })
        
#     linhas_projecao = sorted(linhas_projecao, key=lambda x: x['categoria'].lower())

#     return render(request, 'financas/projecao.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'meses_colunas': meses_colunas,
#         'linhas_projecao': linhas_projecao,
#         'totais_colunas': totais_colunas,
#         'ano_base': ano_base,
#         'mes_base': mes_base,
#         'mes_base_nome': f"{nomes_meses[mes_base]}/{ano_base}",
#         'ano_anterior': data_anterior.year,
#         'mes_anterior': data_anterior.month,
#         'ano_posterior': data_posterior.year,
#         'mes_posterior': data_posterior.month,
#     })

# ==========================================
# HISTÓRICO
# ==========================================
@login_required
def historico_lista(request):
    meses_fechados = Mes.objects.filter(fechado=True).order_by('-ano', '-mes')
    return render(request, 'financas/historico_lista.html', {'meses': meses_fechados})

@login_required
def historico_detalhe(request, mes_id):
    mes = Mes.objects.get(id=mes_id)
    receitas = Receita.objects.filter(mes=mes)
    gastos = Gasto.objects.filter(mes=mes)
    
    total_receitas = receitas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    total_gastos = gastos.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    sobra = total_receitas - total_gastos
    
    return render(request, 'financas/historico_detalhe.html', {
        'mes': mes,
        'receitas': receitas,
        'gastos': gastos,
        'total_receitas': total_receitas,
        'total_gastos': total_gastos,
        'sobra': sobra,
    })

# ==========================================
# COFRE (DÍVIDAS E RESERVA)
# ==========================================
@login_required
def cofre(request):
    dividas = Divida.objects.filter(ativo=True)
    reserva = ReservaEmergencia.objects.first()
    
    if not reserva:
        reserva = ReservaEmergencia.objects.create()
    
    form_divida = DividaForm()
    form_reserva = ReservaForm(instance=reserva)

    total_gastos_historico = Gasto.objects.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    meses_registrados = Mes.objects.count()
    custo_vida_medio = total_gastos_historico / meses_registrados if meses_registrados > 0 else Decimal('0')
    
    meta_reserva = custo_vida_medio * reserva.meses_alvo
    pct_reserva = (reserva.valor_guardado / meta_reserva * 100) if meta_reserva > 0 else 0
    total_divida = sum(d.falta_pagar for d in dividas)

    if request.method == 'POST':
        if 'salvar_divida' in request.POST:
            form_divida = DividaForm(request.POST)
            if form_divida.is_valid():
                form_divida.save()
                messages.success(request, 'Dívida cadastrada!')
                return redirect('cofre')
        
        elif 'salvar_reserva' in request.POST:
            form_reserva = ReservaForm(request.POST, instance=reserva)
            if form_reserva.is_valid():
                form_reserva.save()
                messages.success(request, 'Reserva atualizada!')
                return redirect('cofre')

    return render(request, 'financas/cofre.html', {
        'dividas': dividas,
        'reserva': reserva,
        'form_divida': form_divida,
        'form_reserva': form_reserva,
        'total_divida': total_divida,
        'custo_vida_medio': custo_vida_medio,
        'meta_reserva': meta_reserva,
        'pct_reserva': float(pct_reserva),
    })

@login_required
def divida_excluir(request, divida_id):
    divida = Divida.objects.get(id=divida_id)
    if request.method == 'POST':
        divida.delete()
        messages.success(request, 'Dívida removida!')
    return redirect('cofre')

# ---------- RELATÓRIOS ----------
# ---------- RELATÓRIOS ----------
@login_required
def relatorios(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return render(request, 'financas/relatorios.html', {'sem_mes_ativo': True})

    mes_ativo = Mes.objects.get(id=mes_ativo_id)

    # 1. Gastos por Pessoa
    gastos_por_pessoa = Gasto.objects.filter(mes=mes_ativo).values('pessoa__nome').annotate(
        total=Sum('valor')
    ).order_by('-total')

    # 2. Agrupamento Inteligente (Mês Atual)
    gastos_mes = Gasto.objects.filter(mes=mes_ativo)
    total_gasto_mes = sum(g.valor for g in gastos_mes)
    
    agrupado_mes = {}
    for g in gastos_mes:
        nome_limpo = re.sub(r'\s*\(\d+/\d+\)|\s*-\s*Parcela\s*\d+/\d+', '', g.descricao).strip()
        
        if g.cartao:
            chave = f"{nome_limpo} ({g.cartao.nome})"
            tipo_visual = 'Cartão'
        else:
            chave = g.categoria.nome
            tipo_visual = 'Essencial' if g.categoria.tipo == 'E' else 'Não Essencial'

        if chave not in agrupado_mes:
            agrupado_mes[chave] = {'nome': chave, 'tipo': tipo_visual, 'total': Decimal('0')}
        
        agrupado_mes[chave]['total'] += g.valor

    top_categorias = sorted(agrupado_mes.values(), key=lambda x: x['total'], reverse=True)[:5]

    # 3. Média de Gastos (Últimos 3 meses)
    ultimos_meses = Mes.objects.filter(gastos__isnull=False).order_by('-ano', '-mes')[:3]
    media_categorias = []
    if ultimos_meses:
        ids_meses = [m.id for m in ultimos_meses]
        gastos_agrupados = Gasto.objects.filter(mes__id__in=ids_meses).values(
            'categoria__nome'
        ).annotate(
            total=Sum('valor')
        ).order_by('-total')[:5] 

        for item in gastos_agrupados:
            media = item['total'] / 3
            media_categorias.append({
                'nome': item['categoria__nome'],
                'media': media
            })

    # 4. LISTA COMPLETA DE GASTOS
    lista_completa_gastos = Gasto.objects.filter(mes=mes_ativo).order_by('-data', '-id')

    # 5. DICAS DE ECONOMIA (A MÁGICA AQUI)
    dicas = []
    
    # Dica 1: Se a maior categoria de cartão passar de 30% do total
    if top_categorias and top_categorias[0]['tipo'] == 'Cartão':
        if top_categorias[0]['total'] > (total_gasto_mes * Decimal('0.3')):
            dicas.append(f"Você gastou mais de 30% do seu dinheiro em '{top_categorias[0]['nome']}'. Tente negociar ou evitar novas compras nesse local.")

    # Dica 2: Se gastou mais do que tem de receita (ou renda)
    # (Vou pegar a receita total para comparar)
    total_receitas = Receita.objects.filter(mes=mes_ativo).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    if total_gasto_mes > total_receitas and total_receitas > 0:
        dicas.append("Atenção! Seus gastos passaram das suas receitas este mês. Reveja os gastos não essenciais.")

    # Dica 3: Se tem categoria passando do limite (usando a lógica que já criamos)
    categorias_estouradas = Categoria.objects.filter(ativo=True, limite_mensal__isnull=False)
    for cat in categorias_estouradas:
        gasto_cat = Gasto.objects.filter(mes=mes_ativo, categoria=cat).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        if gasto_cat > cat.limite_mensal:
            dicas.append(f"O orçamento de '{cat.nome}' estourou! Você gastou R$ {gasto_cat} mas o limite era R$ {cat.limite_mensal}.")

    # Dica 4: Genérica se não houver alertas (Economia positiva)
    if not dicas:
        dicas.append("Parabéns! Suas contas parecem equilibradas este mês. Que tal guardar a sobra na sua Reserva de Emergência?")

    # Pega só as 3 primeiras dicas pra não poluir a tela
    dicas = dicas[:3]

    return render(request, 'financas/relatorios.html', {
        'sem_mes_ativo': False,
        'mes_ativo': mes_ativo,
        'gastos_por_pessoa': gastos_por_pessoa,
        'top_categorias': top_categorias,
        'media_categorias': media_categorias,
        'lista_completa_gastos': lista_completa_gastos,
        'total_gasto_mes': total_gasto_mes,
        'dicas': dicas,
    })

# @login_required
# def relatorios(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return render(request, 'financas/relatorios.html', {'sem_mes_ativo': True})

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)

#     # 1. Gastos por Pessoa
#     gastos_por_pessoa = Gasto.objects.filter(mes=mes_ativo).values('pessoa__nome').annotate(
#         total=Sum('valor')
#     ).order_by('-total')

#     # 2. Top 5 Categorias (Mês Atual)
#     top_categorias = Gasto.objects.filter(mes=mes_ativo).values('categoria__nome', 'categoria__tipo').annotate(
#         total=Sum('valor')
#     ).order_by('-total')[:5]

#     # 3. Média de Gastos por Categoria (Últimos 3 meses)
#     # Vamos pegar os últimos 3 meses que tiveram gastos
#     ultimos_meses = Mes.objects.filter(gastos__isnull=False).order_by('-ano', '-mes')[:3]
    
#     media_categorias = []
#     if ultimos_meses:
#         # Pega os IDs desses meses
#         ids_meses = [m.id for m in ultimos_meses]
        
#         # Agrupa os gastos por categoria, soma tudo e divide pelo número de meses (3)
#         gastos_agrupados = Gasto.objects.filter(mes__id__in=ids_meses).values(
#             'categoria__nome', 'categoria__tipo'
#         ).annotate(
#             total=Sum('valor')
#         ).order_by('-total')[:5] # Pegar as 5 maiores médias

#         for item in gastos_agrupados:
#             media = item['total'] / 3
#             media_categorias.append({
#                 'nome': item['categoria__nome'],
#                 'tipo': item['categoria__tipo'],
#                 'media': media
#             })

#     return render(request, 'financas/relatorios.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'gastos_por_pessoa': gastos_por_pessoa,
#         'top_categorias': top_categorias,
#         'media_categorias': media_categorias,
#     })

# ---------- EXPORTAR RELATÓRIO EXCEL ----------
@login_required
def exportar_relatorio(request):
    mes_ativo_id = request.session.get('mes_ativo_id')
    if not mes_ativo_id:
        return redirect('mes_lista')

    mes_ativo = Mes.objects.get(id=mes_ativo_id)
    
    # --- BUSCANDO DADOS ---
    gastos = Gasto.objects.filter(mes=mes_ativo).order_by('-data')
    total_gasto_mes = sum(g.valor for g in gastos)
    
    # Agrupamento para o gráfico
    gastos_por_categoria = Gasto.objects.filter(mes=mes_ativo).values('categoria__nome').annotate(
        total=Sum('valor')
    ).order_by('-total')

    # Projeção dos próximos 6 meses
    meses_futuros = Mes.objects.filter(
        (models.Q(ano__gt=mes_ativo.ano) | models.Q(ano=mes_ativo.ano, mes__gt=mes_ativo.mes))
    ).order_by('ano', 'mes')[:6]

    projecao_dados = []
    for m in meses_futuros:
        g_total = Gasto.objects.filter(mes=m).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        r_total = Receita.objects.filter(mes=m).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        sobra = r_total - g_total
        projecao_dados.append({
            'nome': f"{m.mes}/{m.ano}",
            'gasto': g_total,
            'receita': r_total,
            'sobra': sobra
        })

    # --- CRIA O EXCEL ---
    wb = openpyxl.Workbook()
    
    # ==========================================
    # ABA 1: DASHBOARD & GRÁFICOS
    # ==========================================
    ws1 = wb.active
    ws1.title = "Dashboard"
    
    # Título
    ws1['A1'] = f"RELATÓRIO FINANCEIRO - {mes_ativo}"
    ws1['A1'].font = Font(name='Calibri', bold=True, size=16, color='1E1B4B')
    ws1.merge_cells('A1:F1')

    # Dados ocultos para o gráfico de pizza (Coloca na coluna E e F para não atrapalhar o visual)
    ws1['E2'] = "Categoria"
    ws1['F2'] = "Valor"
    for i, item in enumerate(gastos_por_categoria, start=3):
        ws1[f'E{i}'] = item['categoria__nome']
        ws1[f'F{i}'] = float(item['total'])

    # Criando o Gráfico de Pizza (Rosca)
    pie = PieChart()
    labels = Reference(ws1, min_col=5, min_row=3, max_row=2 + len(gastos_por_categoria))
    data = Reference(ws1, min_col=6, min_row=2, max_row=2 + len(gastos_por_categoria))
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(labels)
    pie.title = "Divisão de Gastos por Categoria"
    ws1.add_chart(pie, "A3")

    # ==========================================
    # ABA 2: PROJEÇÃO E DICAS
    # ==========================================
    ws2 = wb.create_sheet(title="Projeção 6 Meses")
    
    ws2['A1'] = "PROJEÇÃO INTELIGENTE (PRÓXIMOS MESES)"
    ws2['A1'].font = Font(name='Calibri', bold=True, size=14, color='1E1B4B')
    
    # Tabela de Projeção
    headers_proj = ["Mês", "Gastos Previstos", "Receitas Previstas", "Sobra"]
    for col, text in enumerate(headers_proj, start=1):
        c = ws2.cell(row=3, column=col, value=text)
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill(start_color='8B5CF6', end_color='8B5CF6', fill_type='solid')
        c.alignment = Alignment(horizontal='center')

    for i, p in enumerate(projecao_dados, start=4):
        ws2.cell(row=i, column=1, value=p['nome']).alignment = Alignment(horizontal='center')
        ws2.cell(row=i, column=2, value=float(p['gasto'])).number_format = 'R$ #,##0.00'
        ws2.cell(row=i, column=3, value=float(p['receita'])).number_format = 'R$ #,##0.00'
        ws2.cell(row=i, column=4, value=float(p['sobra'])).number_format = 'R$ #,##0.00'

    # Gráfico de Barras da Projeção
    bar = BarChart()
    bar.type = "col"
    bar.style = 10
    bar.title = "Fluxo de Caixa Futuro"
    data_bar = Reference(ws2, min_col=2, max_col=3, min_row=3, max_row=3 + len(projecao_dados))
    cats_bar = Reference(ws2, min_col=1, min_row=4, max_row=3 + len(projecao_dados))
    bar.add_data(data_bar, titles_from_data=True)
    bar.set_categories(cats_bar)
    ws2.add_chart(bar, "F3") # Joga o gráfico pro lado

    # Quadro de Dicas
    ws2['A15'] = "💡 DICAS DE ECONOMIA E MELHORIA"
    ws2['A15'].font = Font(bold=True, size=12, color='DC2626')
    
    dicas_texto = [
        "1. Analise as categorias do gráfico de rosca. Onde há maior fatia?",
        "2. Tente reduzir em 10% o maior gasto não essencial deste mês.",
        "3. Compare a coluna 'Receitas' com 'Gastos' na projeção acima.",
        "4. Se a projeção mostrar meses no negativo, reveja compras parceladas.",
        "5. Não se esqueça de alimentar a Reserva de Emergência no sistema."
    ]
    for i, dica in enumerate(dicas_texto, start=16):
        ws2.cell(row=i, column=1, value=dica).font = Font(italic=True, color='475569')

    # ==========================================
    # ABA 3: EXTRATO DETALHADO
    # ==========================================
    ws3 = wb.create_sheet(title="Extrato Detalhado")
    
    ws3['A1'] = f"EXTRATO DE GASTOS - {mes_ativo}"
    ws3['A1'].font = Font(bold=True, size=14, color='1E1B4B')
    ws3.merge_cells('A1:E1')

    headers_ext = ['Data', 'Descrição', 'Pessoa', 'Categoria', 'Valor']
    for col, text in enumerate(headers_ext, start=1):
        c = ws3.cell(row=3, column=col, value=text)
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill(start_color='EC4899', end_color='EC4899', fill_type='solid')
        c.alignment = Alignment(horizontal='center')

    for i, g in enumerate(gastos, start=4):
        ws3.cell(row=i, column=1, value=g.data.strftime('%d/%m/%Y'))
        ws3.cell(row=i, column=2, value=g.descricao)
        ws3.cell(row=i, column=3, value=g.pessoa.nome)
        ws3.cell(row=i, column=4, value=g.categoria.nome)
        c_val = ws3.cell(row=i, column=5, value=float(g.valor))
        c_val.number_format = 'R$ #,##0.00'
        c_val.font = Font(color='DC2626', bold=True)

    # Total
    linha_total = 4 + len(gastos)
    ws3.cell(row=linha_total, column=4, value="TOTAL:").font = Font(bold=True)
    c_tot = ws3.cell(row=linha_total, column=5, value=float(total_gasto_mes))
    c_tot.number_format = 'R$ #,##0.00'
    c_tot.font = Font(bold=True, color='DC2626')

    # Ajustar colunas
    # Ajustar colunas (com proteção para células mescladas)
     # Ajustar colunas (com proteção para células mescladas)
    for ws in [ws1, ws2, ws3]:
        for col in ws.columns:
            # Pega a primeira célula da coluna
            cell_inicial = col[0]
            
            # Se a primeira célula for mesclada, pula ela (pra não dar erro)
            if not hasattr(cell_inicial, 'column_letter'):
                continue
                
            max_length = 0
            column_letter = cell_inicial.column_letter
            
            for cell in col:
                try:
                    if hasattr(cell, 'value') and cell.value is not None:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                except:
                    pass
                    
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

    # Prepara Download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Relatorio_Profissional_{mes_ativo.ano}_{mes_ativo.mes}.xlsx"'
    
    wb.save(response)
    return response

# @login_required
# def exportar_relatorio(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return redirect('mes_lista')

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
#     gastos = Gasto.objects.filter(mes=mes_ativo).order_by('-data')

#     # Cria um novo arquivo Excel
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = f"Relatório {mes_ativo.mes}-{mes_ativo.ano}"

#     # --- DEFINIÇÃO DE ESTILOS (PALETA BULLET JOURNAL) ---
#     cor_borda = Side(style='medium', color='FF222222')
#     borda = Border(left=cor_borda, right=cor_borda, top=cor_borda, bottom=cor_borda)

#     fundo_header = PatternFill(start_color='FFA8C8F0', end_color='FFA8C8F0', fill_type='solid') # Azul pastel
#     fundo_total = PatternFill(start_color='FFF7B2BD', end_color='FFF7B2BD', fill_type='solid') # Rosa pastel
#     fundo_card = PatternFill(start_color='FFD1B3E2', end_color='FFD1B3E2', fill_type='solid') # Roxo pastel
#     fundo_essencial = PatternFill(start_color='FFB4E3D3', end_color='FFB4E3D3', fill_type='solid') # Verde pastel

#     fonte_header = Font(name='Arial', bold=True, color='FF222222', size=12)
#     fonte_normal = Font(name='Arial', color='FF333333', size=11)
#     fonte_bold = Font(name='Arial', bold=True, color='FF333333', size=11)

#     alinhamento_centro = Alignment(horizontal='center', vertical='center')
#     alinhamento_direita = Alignment(horizontal='right', vertical='center')
#     alinhamento_esquerda = Alignment(horizontal='left', vertical='center')

#     # --- TÍTULO DO RELATÓRIO ---
#     ws.merge_cells('A1:E1')
#     ws['A1'] = f"RELATÓRIO FINANCEIRO - {mes_ativo}"
#     ws['A1'].font = Font(name='Arial', bold=True, size=16, color='FF222222')
#     ws['A1'].alignment = alinhamento_centro

#     # --- CABEÇALHO DA TABELA ---
#     headers = ['Data', 'Descrição', 'Pessoa', 'Categoria', 'Valor (R$)']
#     ws.append(headers) # Linha 2

#     for col, text in enumerate(headers, start=1):
#         cell = ws.cell(row=2, column=col)
#         cell.fill = fundo_header
#         cell.font = fonte_header
#         cell.alignment = alinhamento_centro
#         cell.border = borda

#     # --- LINHAS DE DADOS ---
#     row_num = 3
#     for g in gastos:
#         ws.cell(row=row_num, column=1, value=g.data.strftime('%d/%m/%Y')).alignment = alinhamento_centro
        
#         desc = g.descricao
#         if g.cartao:
#             desc += f" ({g.cartao.nome})"
#         ws.cell(row=row_num, column=2, value=desc).alignment = alinhamento_esquerda
        
#         ws.cell(row=row_num, column=3, value=g.pessoa.nome).alignment = alinhamento_esquerda
        
#         # Categoria com cor
#         cat_cell = ws.cell(row=row_num, column=4, value=g.categoria.nome)
#         cat_cell.alignment = alinhamento_centro
#         if g.categoria.tipo == 'E':
#             cat_cell.fill = fundo_essencial
#         else:
#             cat_cell.fill = fundo_header

#         val_cell = ws.cell(row=row_num, column=5, value=float(g.valor))
#         val_cell.number_format = 'R$ #,##0.00'
#         val_cell.alignment = alinhamento_direita
#         val_cell.font = Font(name='Arial', color='FFDC2626', size=11, bold=True) # Vermelho

#         # Aplica borda em todas as células da linha
#         for col in range(1, 6):
#             ws.cell(row=row_num, column=col).border = borda
#             if not ws.cell(row=row_num, column=col).font.bold:
#                 ws.cell(row=row_num, column=col).font = fonte_normal

#         row_num += 1

#     # --- LINHA DE TOTAL ---
#     ws.cell(row=row_num, column=1, value="").border = borda
#     ws.cell(row=row_num, column=2, value="").border = borda
#     ws.cell(row=row_num, column=3, value="").border = borda
    
#     total_cell = ws.cell(row=row_num, column=4, value="SOMA TOTAL:")
#     total_cell.font = fonte_bold
#     total_cell.alignment = alinhamento_direita
#     total_cell.border = borda
#     total_cell.fill = fundo_total

#     valor_total = sum(g.valor for g in gastos)
#     val_total_cell = ws.cell(row=row_num, column=5, value=float(valor_total))
#     val_total_cell.number_format = 'R$ #,##0.00'
#     val_total_cell.alignment = alinhamento_direita
#     val_total_cell.font = fonte_bold
#     val_total_cell.border = borda
#     val_total_cell.fill = fundo_total

#     # --- AJUSTE DE LARGURA DAS COLUNAS ---
#     ws.column_dimensions['A'].width = 15
#     ws.column_dimensions['B'].width = 40
#     ws.column_dimensions['C'].width = 15
#     ws.column_dimensions['D'].width = 20
#     ws.column_dimensions['E'].width = 15

#     # --- PREPARA O DOWNLOAD ---
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename="relatorio_{mes_ativo.ano}_{mes_ativo.mes}.xlsx"'
    
#     wb.save(response)
#     return response