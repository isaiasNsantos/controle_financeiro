
# import pdfplumber
# import re
# import json
# from datetime import datetime, date
# from decimal import Decimal
# from dateutil.relativedelta import relativedelta
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.db.models import Sum
# from .models import (Pessoa, Categoria, FormaPagamento, Mes, Receita, Gasto, Cartao, Divida, ReservaEmergencia)
# from .forms import (PessoaForm, CategoriaForm, FormaPagamentoForm, MesForm, ReceitaForm, GastoForm, CartaoForm, DividaForm, ReservaForm)
# from dateutil.relativedelta import relativedelta
# from django.contrib.auth.decorators import login_required

# # ---------- PESSOAS ----------
# @login_required
# def pessoa_lista(request):
#     pessoas = Pessoa.objects.all()
#     form = PessoaForm()
#     return render(request, 'financas/pessoa_lista.html', {'pessoas': pessoas, 'form': form})

# @login_required
# def pessoa_criar(request):
#     if request.method == 'POST':
#         form = PessoaForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('pessoa_lista')
#     else:
#         form = PessoaForm()
#     return render(request, 'financas/pessoa_lista.html', {
#         'pessoas': Pessoa.objects.all(),
#         'form': form,
#     })


# # ---------- CATEGORIAS ----------
# def categoria_lista(request):
#     categorias = Categoria.objects.all()
#     form = CategoriaForm()
#     return render(request, 'financas/categoria_lista.html', {'categorias': categorias, 'form': form})


# def categoria_criar(request):
#     if request.method == 'POST':
#         form = CategoriaForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('categoria_lista')
#     else:
#         form = CategoriaForm()
#     return render(request, 'financas/categoria_lista.html', {
#         'categorias': Categoria.objects.all(),
#         'form': form,
#     })


# # ---------- FORMAS DE PAGAMENTO ----------
# def formapagamento_lista(request):
#     formas = FormaPagamento.objects.all()
#     form = FormaPagamentoForm()
#     return render(request, 'financas/formapagamento_lista.html', {'formas': formas, 'form': form})


# def formapagamento_criar(request):
#     if request.method == 'POST':
#         form = FormaPagamentoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('formapagamento_lista')
#     else:
#         form = FormaPagamentoForm()
#     return render(request, 'financas/formapagamento_lista.html', {
#         'formas': FormaPagamento.objects.all(),
#         'form': form,
#     })


# # ---------- MESES ----------
# def mes_lista(request):
#     # Pega só os meses que estão abertos
#     meses = Mes.objects.filter(fechado=False).order_by('-ano', '-mes')
#     form = MesForm()
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     return render(request, 'financas/mes_lista.html', {
#         'meses': meses,
#         'form': form,
#         'mes_ativo_id': mes_ativo_id,
#     })


# def mes_criar(request):
#     if request.method == 'POST':
#         form = MesForm(request.POST)
#         if form.is_valid():
#             novo_mes = form.save(commit=False)
            
#             # Descobre qual foi o último mês que teve receita
#             ultimo_mes_com_receita = Mes.objects.filter(receitas__isnull=False).order_by('-ano', '-mes').first()
            
#             # Se existir um mês anterior, copia as receitas dele
#             if ultimo_mes_com_receita:
#                 receitas_antigas = Receita.objects.filter(mes=ultimo_mes_com_receita)
#                 novo_mes.save() # Salva o mês novo primeiro
                
#                 for r in receitas_antigas:
#                     Receita.objects.create(
#                         mes=novo_mes,
#                         descricao=r.descricao,
#                         valor=r.valor,
#                         data=date(novo_mes.ano, novo_mes.mes, 1), # Dia 1 do novo mês
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

# def mes_selecionar(request, mes_id):
#     if request.method == 'POST':
#         request.session['mes_ativo_id'] = mes_id
#     return redirect('mes_lista')

# # ---------- RECEITAS ----------
# def receita_lista(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return render(request, 'financas/receita_lista.html', {
#             'sem_mes_ativo': True,
#             'receitas': [],
#             'form': None,
#         })

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
#     receitas = Receita.objects.filter(mes=mes_ativo)
#     form = ReceitaForm()

#     total = sum(r.valor for r in receitas)

#     return render(request, 'financas/receita_lista.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'receitas': receitas,
#         'form': form,
#         'total': total,
#     })


# def receita_criar(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return redirect('mes_lista')

#     if request.method == 'POST':
#         form = ReceitaForm(request.POST)
#         if form.is_valid():
#             receita = form.save(commit=False)
#             receita.mes = Mes.objects.get(id=mes_ativo_id)
#             receita.save()
#             return redirect('receita_lista')
#     else:
#         form = ReceitaForm()

#     return render(request, 'financas/receita_lista.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': Mes.objects.get(id=mes_ativo_id),
#         'receitas': Receita.objects.filter(mes_id=mes_ativo_id),
#         'form': form,
#         'total': sum(r.valor for r in Receita.objects.filter(mes_id=mes_ativo_id)),
#     })

# # ---------- GASTOS ----------
# def gasto_lista(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return render(request, 'financas/gasto_lista.html', {
#             'sem_mes_ativo': True,
#             'gastos': [],
#             'form': None,
#         })

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
#     gastos = Gasto.objects.filter(mes=mes_ativo)
#     form = GastoForm()

#     total = sum(g.valor for g in gastos)

#     return render(request, 'financas/gasto_lista.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'gastos': gastos,
#         'form': form,
#         'total': total,
#     })


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




# # ---------- DASHBOARD ----------
# @login_required
# def dashboard(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return render(request, 'financas/dashboard.html', {'sem_mes_ativo': True})

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)

#     # Totais
#     total_receitas = Receita.objects.filter(mes=mes_ativo).aggregate(total=Sum('valor'))['total'] or Decimal('0')
#     total_gastos = Gasto.objects.filter(mes=mes_ativo).aggregate(total=Sum('valor'))['total'] or Decimal('0')
#     verba = total_receitas - total_gastos

#     # Alerta
#     if total_receitas == 0:
#         alerta = 'sem_receita'
#     elif verba < 0:
#         alerta = 'estourado'
#     elif verba < (total_receitas * Decimal('0.10')):
#         alerta = 'apertado'
#     else:
#         alerta = 'ok'

#     # 50-30-20
#     gastos_essenciais = Gasto.objects.filter(
#         mes=mes_ativo, categoria__tipo='E'
#     ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

#     gastos_nao_essenciais = Gasto.objects.filter(
#         mes=mes_ativo, categoria__tipo='N'
#     ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

#     if total_receitas > 0:
#         pct_essenciais = float((gastos_essenciais / total_receitas) * 100)
#         pct_nao_essenciais = float((gastos_nao_essenciais / total_receitas) * 100)
#         pct_sobra = float((verba / total_receitas) * 100)
#     else:
#         pct_essenciais = 0
#         pct_nao_essenciais = 0
#         pct_sobra = 0

#     # Orçamentos por categoria
#     categorias_com_limite = Categoria.objects.filter(
#         ativo=True, limite_mensal__isnull=False
#     ).exclude(limite_mensal=0)

#     orcamentos = []
#     for cat in categorias_com_limite:
#         gasto_cat = Gasto.objects.filter(
#             mes=mes_ativo, categoria=cat
#         ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

#         pct_usado = float((gasto_cat / cat.limite_mensal) * 100) if cat.limite_mensal > 0 else 0
#         restante = cat.limite_mensal - gasto_cat

#         if pct_usado > 100:
#             cor = 'danger'
#         elif pct_usado >= 70:
#             cor = 'warning'
#         else:
#             cor = 'success'

#         orcamentos.append({
#             'categoria': cat,
#             'gasto': gasto_cat,
#             'limite': cat.limite_mensal,
#             'restante': restante,
#             'pct_usado': pct_usado,
#             'cor': cor,
#         })

#     # --- CARTÕES ---
#     cartoes_ativos = Cartao.objects.filter(ativo=True)
#     resumo_cartoes = []
    
#     for c in cartoes_ativos:
#         total_cartao = Gasto.objects.filter(
#             mes=mes_ativo, cartao=c
#         ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
#         resumo_cartoes.append({
#             'cartao': c,
#             'total_mes': total_cartao
#         })

#     # Últimos 5 lançamentos
#     ultimas_receitas = Receita.objects.filter(mes=mes_ativo).order_by('-id')[:5]
#     ultimos_gastos = Gasto.objects.filter(mes=mes_ativo).order_by('-id')[:5]

#     # --- DADOS PARA O GRÁFICO (GASTOS POR CATEGORIA) ---
#     gastos_por_categoria = Gasto.objects.filter(mes=mes_ativo).values('categoria__nome').annotate(
#         total=Sum('valor')
#     ).order_by('-total')

#     grafico_labels = [item['categoria__nome'] for item in gastos_por_categoria]
#     grafico_valores = [float(item['total']) for item in gastos_por_categoria]

#     return render(request, 'financas/dashboard.html', {
#         'sem_mes_ativo': False,
#         'mes_ativo': mes_ativo,
#         'total_receitas': total_receitas,
#         'total_gastos': total_gastos,
#         'verba': verba,
#         'alerta': alerta,
#         'gastos_essenciais': gastos_essenciais,
#         'gastos_nao_essenciais': gastos_nao_essenciais,
#         'pct_essenciais': pct_essenciais,
#         'pct_nao_essenciais': pct_nao_essenciais,
#         'pct_sobra': pct_sobra,
#         'orcamentos': orcamentos,
#         'resumo_cartoes': resumo_cartoes,
#         'ultimas_receitas': ultimas_receitas,
#         'ultimos_gastos': ultimos_gastos,
#         'grafico_labels': grafico_labels,
#         'grafico_valores': grafico_valores,
#     })

# def categoria_excluir(request, categoria_id):
#     categoria = Categoria.objects.get(id=categoria_id)
    
#     if request.method == 'POST':
#         try:
#             categoria.delete()
#             return redirect('categoria_lista')
#         except Exception:
#             # Se der erro (PROTECT), volta pra lista com mensagem
#             return redirect('categoria_lista')
    
#     return redirect('categoria_lista')

# def categoria_excluir(request, categoria_id):
#     categoria = Categoria.objects.get(id=categoria_id)
    
#     if request.method == 'POST':
#         try:
#             nome = categoria.nome
#             categoria.delete()
#             messages.success(request, f'Categoria "{nome}" excluída com sucesso!')
#         except Exception:
#             messages.error(request, f'Não é possível excluir "{categoria.nome}" — ela tem gastos vinculados.')
    
#     return redirect('categoria_lista')

# def categoria_editar(request, categoria_id):
#     categoria = Categoria.objects.get(id=categoria_id)
    
#     if request.method == 'POST':
#         form = CategoriaForm(request.POST, instance=categoria)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Categoria atualizada com sucesso!')
#             return redirect('categoria_lista')
#     else:
#         form = CategoriaForm(instance=categoria)
    
#     return render(request, 'financas/categoria_form.html', {'form': form, 'categoria': categoria})

# # ---------- EXCLUIR / EDITAR RECEITAS ----------
# def receita_excluir(request, receita_id):
#     receita = Receita.objects.get(id=receita_id)
#     if request.method == 'POST':
#         receita.delete()
#         messages.success(request, 'Receita excluída com sucesso!')
#     return redirect('receita_lista')


# def receita_editar(request, receita_id):
#     receita = Receita.objects.get(id=receita_id)
#     if request.method == 'POST':
#         form = ReceitaForm(request.POST, instance=receita)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Receita atualizada com sucesso!')
#             return redirect('receita_lista')
#     else:
#         form = ReceitaForm(instance=receita)
#     return render(request, 'financas/receita_form.html', {'form': form, 'receita': receita})


# # ---------- EXCLUIR / EDITAR GASTOS ----------
# def gasto_excluir(request, gasto_id):
#     gasto = Gasto.objects.get(id=gasto_id)
#     if request.method == 'POST':
#         gasto.delete()
#         messages.success(request, 'Gasto excluído com sucesso!')
#     return redirect('gasto_lista')


# def gasto_editar(request, gasto_id):
#     gasto = Gasto.objects.get(id=gasto_id)
#     if request.method == 'POST':
#         form = GastoForm(request.POST, instance=gasto)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Gasto atualizado com sucesso!')
#             return redirect('gasto_lista')
#     else:
#         form = GastoForm(instance=gasto)
#     return render(request, 'financas/gasto_form.html', {'form': form, 'gasto': gasto})

# # ---------- IMPORTAÇÃO DE FATURA ----------
# def importar_fatura(request):
#     # 1. SE FOR POST E TIVER DADOS DE CONFIRMAÇÃO (Salvar no banco)
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
                
#                 # 1. Salva a parcela ATUAL no mês ativo da fatura
#                 Gasto.objects.create(
#                     mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
#                     categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                 )
                
#                 # 2. Salva as FUTURAS
#                 for j in range(1, parcelas_restantes + 1):
#                     # Avança a data pra frente para descobrir o mês futuro
#                     nova_data = data_gasto + relativedelta(months=j)
#                     # Mas garante que o gasto vai cair no mês seguinte ao mês ativo da fatura
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
#                 # Se não for parcelado, salva normal no mês ativo da fatura
#                 Gasto.objects.create(
#                     mes=mes_ativo, descricao=descricao_limpa, valor=valor, data=data_gasto,
#                     categoria=categoria, pessoa=pessoa, forma_pagamento=forma_credito, cartao=cartao,
#                 )
#             salvos += 1
            
#         messages.success(request, f'{salvos} transações importadas com sucesso!')
#         return redirect('gasto_lista')

#     # 2. SE FOR POST (Ler o PDF)
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

#     # 2. SE FOR POST (Ler o PDF)
#     if request.method == 'POST':
#         pdf_file = request.FILES.get('arquivo_pdf')
#         if not pdf_file:
#             messages.error(request, 'Nenhum arquivo enviado.')
#             return redirect('importar_fatura')

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

#         dados_json = json.dumps(transacoes)
        
#         categorias = Categoria.objects.filter(ativo=True)
#         pessoas = Pessoa.objects.filter(ativo=True)
#         cartoes = Cartao.objects.filter(ativo=True)

#         return render(request, 'financas/importar_fatura.html', {
#             'transacoes': transacoes,
#             'total': sum(Decimal(t['valor']) for t in transacoes),
#             'dados_json': dados_json,
#             'categorias': categorias,
#             'pessoas': pessoas,
#             'cartoes': cartoes,
#         })

#     return render(request, 'financas/importar_fatura.html')


# # ---------- CARTÕES ----------
# def cartao_lista(request):
#     cartoes = Cartao.objects.all()
#     form = CartaoForm()
#     return render(request, 'financas/cartao_lista.html', {'cartoes': cartoes, 'form': form})

# def cartao_criar(request):
#     if request.method == 'POST':
#         form = CartaoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Cartão cadastrado com sucesso!')
#             return redirect('cartao_lista')
#     else:
#         form = CartaoForm()
#     return render(request, 'financas/cartao_lista.html', {
#         'cartoes': Cartao.objects.all(),
#         'form': form,
#     })

# def cartao_editar(request, cartao_id):
#     cartao = Cartao.objects.get(id=cartao_id)
#     if request.method == 'POST':
#         form = CartaoForm(request.POST, instance=cartao)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Cartão atualizado com sucesso!')
#             return redirect('cartao_lista')
#     else:
#         form = CartaoForm(instance=cartao)
#     return render(request, 'financas/cartao_form.html', {'form': form, 'cartao': cartao})

# def cartao_excluir(request, cartao_id):
#     cartao = Cartao.objects.get(id=cartao_id)
#     if request.method == 'POST':
#         try:
#             nome = cartao.nome
#             cartao.delete()
#             messages.success(request, f'Cartão "{nome}" excluído com sucesso!')
#         except Exception:
#             messages.error(request, f'Não é possível excluir "{cartao.nome}" — ele tem gastos vinculados.')
#     return redirect('cartao_lista')

 
# # ---------- PROJEÇÃO 12 MESES ----------
# def projecao(request):
#     mes_ativo_id = request.session.get('mes_ativo_id')
#     if not mes_ativo_id:
#         return render(request, 'financas/projecao.html', {'sem_mes_ativo': True})

#     mes_ativo = Mes.objects.get(id=mes_ativo_id)
    
#     # Pega o ano e mês da URL (se o usuário clicou em Anterior/Próximo)
#     # Se não tiver nada na URL, usa o mês ativo do sistema
#     ano_base = int(request.GET.get('ano', mes_ativo.ano))
#     mes_base = int(request.GET.get('mes', mes_ativo.mes))
    
#     # Dicionário para formatar o nome do mês
#     nomes_meses = {
#         1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
#         7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
#     }

#     meses_colunas = []
#     data_atual = date(ano_base, mes_base, 1)
    
#     # Cria as 12 colunas
#     for i in range(12):
#         mes_alvo = data_atual + relativedelta(months=i)
#         meses_colunas.append({
#             'id': f"{mes_alvo.year}-{mes_alvo.month}",
#             'nome': f"{nomes_meses[mes_alvo.month]}/{mes_alvo.year}", 
#             'ano': mes_alvo.year,
#             'mes': mes_alvo.month,
#         })

#     # Calcula os botões de navegação
#     data_anterior = data_atual - relativedelta(months=1)
#     data_posterior = data_atual + relativedelta(months=1)
    
#     # Pega os gastos de todos os anos que estão na tabela
#     anos_filtro = list(set([m['ano'] for m in meses_colunas]))
    
#     gastos_periodo = Gasto.objects.filter(
#         mes__ano__in=anos_filtro
#     ).select_related('mes', 'cartao')

#     agrupado = {}
#     totais_colunas = {m['id']: Decimal('0') for m in meses_colunas}

#     for g in gastos_periodo:
#         # Monta a chave do mês (ex: "2026-10")
#         id_mes = f"{g.mes.ano}-{g.mes.mes}"
        
#         # Se o gasto não for de um dos 12 meses que estamos mostrando, ignora
#         if id_mes not in totais_colunas:
#             continue

#         # Limpa a descrição pra agrupar as parcelas (ex: "Jim.Com - Parcela 1/5" vira "Jim.Com")
#         nome_limpo = re.sub(r'- Parcela \d+/\d+', '', g.descricao).strip()
#         if not nome_limpo:
#             nome_limpo = g.descricao
            
#         if nome_limpo not in agrupado:
#             agrupado[nome_limpo] = {}
            
#         if id_mes not in agrupado[nome_limpo]:
#             agrupado[nome_limpo][id_mes] = Decimal('0')
            
#         agrupado[nome_limpo][id_mes] += g.valor
#         totais_colunas[id_mes] += g.valor

#     # Transforma em lista e ordena alfabeticamente
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

# from dateutil.relativedelta import relativedelta

# # ... (suas outras views)

# # ---------- FECHAR MÊS ----------
# def mes_fechar(request, mes_id):
#     if request.method == 'POST':
#         mes_atual = Mes.objects.get(id=mes_id)
        
#         if mes_atual.fechado:
#             return redirect('mes_lista')

#         # 1. Marca o mês atual como fechado
#         mes_atual.fechado = True
#         mes_atual.save()

#         # 2. Descobre qual é o próximo mês
#         data_atual = date(mes_atual.ano, mes_atual.mes, 1)
#         data_proximo = data_atual + relativedelta(months=1)

#         # 3. Cria o próximo mês (se não existir)
#         proximo_mes, criado = Mes.objects.get_or_create(
#             ano=data_proximo.year,
#             mes=data_proximo.month,
#             defaults={'fechado': False}
#         )

#         # 4. Copia as receitas do mês atual para o próximo (se ele acabou de ser criado)
#         if criado:
#             receitas_antigas = Receita.objects.filter(mes=mes_atual)
#             for r in receitas_antigas:
#                 Receita.objects.create(
#                     mes=proximo_mes,
#                     descricao=r.descricao,
#                     valor=r.valor,
#                     data=data_proximo, # Coloca a data como o dia 1 do novo mês
#                     pessoa=r.pessoa
#                 )
#             messages.success(request, f'Mês {mes_atual} fechado! As receitas foram copiadas para {proximo_mes}.')
#         else:
#             messages.success(request, f'Mês {mes_atual} fechado! O mês {proximo_mes} já estava aberto.')

#         # 5. Já muda o "mês ativo" da sessão para o novo mês
#         request.session['mes_ativo_id'] = proximo_mes.id

#     return redirect('mes_lista')

# # ---------- HISTÓRICO ----------
# def historico_lista(request):
#     # Pega apenas os meses fechados, do mais novo pro mais antigo
#     meses_fechados = Mes.objects.filter(fechado=True).order_by('-ano', '-mes')
#     return render(request, 'financas/historico_lista.html', {'meses': meses_fechados})

# def historico_detalhe(request, mes_id):
#     mes = Mes.objects.get(id=mes_id)
    
#     # Pega os dados daquele mês
#     receitas = Receita.objects.filter(mes=mes)
#     gastos = Gasto.objects.filter(mes=mes)
    
#     total_receitas = receitas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
#     total_gastos = gastos.aggregate(total=Sum('valor'))['total'] or Decimal('0')
#     sobra = total_receitas - total_gastos
    
#     return render(request, 'financas/historico_detalhe.html', {
#         'mes': mes,
#         'receitas': receitas,
#         'gastos': gastos,
#         'total_receitas': total_receitas,
#         'total_gastos': total_gastos,
#         'sobra': sobra,
#     })

# # ---------- COFRE (DÍVIDAS E RESERVA) ----------
# def cofre(request):
#     dividas = Divida.objects.filter(ativo=True)
#     reserva = ReservaEmergencia.objects.first() # Pega a única reserva (só vai ter uma)
    
#     # Se não existir, cria uma reserva zerada
#     if not reserva:
#         reserva = ReservaEmergencia.objects.create()
    
#     form_divida = DividaForm()
#     form_reserva = ReservaForm(instance=reserva)

#     # --- Cálculo da Reserva ---
#     # Pega o gasto médio dos últimos 3 meses fechados (ou abertos se não tiver fechados)
#     # Pra não complicar, vamos pegar a média de gastos de todos os meses registrados
#     total_gastos_historico = Gasto.objects.aggregate(total=Sum('valor'))['total'] or Decimal('0')
#     meses_registrados = Mes.objects.count()
#     custo_vida_medio = total_gastos_historico / meses_registrados if meses_registrados > 0 else Decimal('0')
    
#     meta_reserva = custo_vida_medio * reserva.meses_alvo
#     pct_reserva = (reserva.valor_guardado / meta_reserva * 100) if meta_reserva > 0 else 0

#     # --- Cálculo das Dívidas ---
#     total_divida = sum(d.falta_pagar for d in dividas)

#     if request.method == 'POST':
#         # Se o formulário for de Dívida
#         if 'salvar_divida' in request.POST:
#             form_divida = DividaForm(request.POST)
#             if form_divida.is_valid():
#                 form_divida.save()
#                 messages.success(request, 'Dívida cadastrada!')
#                 return redirect('cofre')
        
#         # Se o formulário for de Reserva
#         elif 'salvar_reserva' in request.POST:
#             form_reserva = ReservaForm(request.POST, instance=reserva)
#             if form_reserva.is_valid():
#                 form_reserva.save()
#                 messages.success(request, 'Reserva atualizada!')
#                 return redirect('cofre')

#     return render(request, 'financas/cofre.html', {
#         'dividas': dividas,
#         'reserva': reserva,
#         'form_divida': form_divida,
#         'form_reserva': form_reserva,
#         'total_divida': total_divida,
#         'custo_vida_medio': custo_vida_medio,
#         'meta_reserva': meta_reserva,
#         'pct_reserva': float(pct_reserva),
#     })

# def divida_excluir(request, divida_id):
#     divida = Divida.objects.get(id=divida_id)
#     if request.method == 'POST':
#         divida.delete()
#         messages.success(request, 'Dívida removida!')
#     return redirect('cofre')

# # ---------- CLONAR MÊS ----------
# def mes_clonar(request, mes_id):
#     if request.method == 'POST':
#         mes_atual = Mes.objects.get(id=mes_id)
        
#         # Descobre qual é o mês anterior (na data)
#         data_atual = date(mes_atual.ano, mes_atual.mes, 1)
#         data_anterior = data_atual - relativedelta(months=1)
        
#         # Tenta achar o mês anterior no banco
#         mes_anterior = Mes.objects.filter(ano=data_anterior.year, mes=data_anterior.month).first()
        
#         if not mes_anterior:
#             messages.error(request, 'Não encontrei o mês anterior para clonar.')
#             return redirect('mes_lista')

#         # 1. Copia as Receitas
#         receitas_antigas = Receita.objects.filter(mes=mes_anterior)
#         for r in receitas_antigas:
#             Receita.objects.create(
#                 mes=mes_atual,
#                 descricao=r.descricao,
#                 valor=r.valor,
#                 data=date(mes_atual.ano, mes_atual.mes, 1), # Joga pro dia 1
#                 pessoa=r.pessoa
#             )

#         # 2. Copia os Gastos (EXCETO os de Cartão)
#         gastos_antigos = Gasto.objects.filter(mes=mes_anterior, cartao__isnull=True)
#         for g in gastos_antigos:
#             Gasto.objects.create(
#                 mes=mes_atual,
#                 descricao=g.descricao,
#                 valor=g.valor,
#                 data=date(mes_atual.ano, mes_atual.mes, 1), # Joga pro dia 1
#                 categoria=g.categoria,
#                 pessoa=g.pessoa,
#                 forma_pagamento=g.forma_pagamento,
#                 cartao=None
#             )

#         messages.success(request, f'Mês clonado com sucesso a partir de {mes_anterior}!')
#         return redirect('mes_lista')

#     return redirect('mes_lista')

# def mes_reabrir(request, mes_id):
#     if request.method == 'POST':
#         mes = Mes.objects.get(id=mes_id)
#         mes.fechado = False
#         mes.save()
#         messages.success(request, f'Mês {mes} reaberto com sucesso!')
#     return redirect('mes_lista')

import pdfplumber
import re
import json
from datetime import datetime, date
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import (Pessoa, Categoria, FormaPagamento, Mes, Receita, Gasto, Cartao, Divida, ReservaEmergencia)
from .forms import (PessoaForm, CategoriaForm, FormaPagamentoForm, MesForm, ReceitaForm, GastoForm, CartaoForm, DividaForm, ReservaForm)

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
            # Pega os dados do formulário
            gasto_base = form.save(commit=False)
            gasto_base.mes = Mes.objects.get(id=mes_ativo_id)
            
            # Lê a quantidade de parcelas (se não preencher, é 1)
            parcelas = form.cleaned_data.get('parcelas') or 1
            valor_total = gasto_base.valor
            
            if parcelas > 1:
                # Divide o valor total pelo número de parcelas
                valor_parcela = valor_total / parcelas
                # Arredonda pra 2 casas decimais (Ex: 3333.33)
                valor_parcela = round(valor_parcela, 2)
                
                data_base = gasto_base.data
                
                for i in range(parcelas):
                    # 1. Cria uma cópia do objeto base
                    novo_gasto = Gasto.objects.create(
                        mes=gasto_base.mes, # Vamos atualizar isso abaixo
                        descricao=f"{gasto_base.descricao} ({i+1}/{parcelas})",
                        valor=valor_parcela,
                        data=data_base,
                        categoria=gasto_base.categoria,
                        pessoa=gasto_base.pessoa,
                        forma_pagamento=gasto_base.forma_pagamento,
                        cartao=gasto_base.cartao
                    )
                    
                    # 2. Joga a data e o mês para frente (se for a partir da 2ª parcela)
                    if i > 0:
                        nova_data = data_base + relativedelta(months=i)
                        novo_mes, _ = Mes.objects.get_or_create(ano=nova_data.year, mes=nova_data.month)
                        novo_gasto.data = nova_data
                        novo_gasto.mes = novo_mes
                        novo_gasto.save()
                        
            else:
                # Se for só 1 parcela, salva normal
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
@login_required
def importar_fatura(request):
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

    if request.method == 'POST' and request.FILES.get('arquivo_pdf'):
        pdf_file = request.FILES.get('arquivo_pdf')
        transacoes = []
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    texto = page.extract_text()
                    if not texto or ("TRANSACÕES" not in texto and "TRANSAÇÕES" not in texto):
                        continue
                        
                    linhas = texto.split('\n')
                    for linha in linhas:
                        match = re.match(r'^(\d{2}\s[A-Z]{3})\s+(.*?)\s+R\$\s*([\d\.]+,\d{2})', linha)
                        if match:
                            data_str = match.group(1)
                            descricao = match.group(2).strip()
                            valor_str = match.group(3)
                            
                            if "Pagamento" in descricao:
                                continue
                            
                            valor_limpo = valor_str.replace('.', '').replace(',', '.')
                            valor = Decimal(valor_limpo)
                            
                            meses = {'JAN':1, 'FEV':2, 'MAR':3, 'ABR':4, 'MAI':5, 'JUN':6, 'JUL':7, 'AGO':8, 'SET':9, 'OUT':10, 'NOV':11, 'DEZ':12}
                            dia, mes_abrev = data_str.split()
                            mes = meses.get(mes_abrev, 1)
                            ano = datetime.now().year
                            data_gasto = date(ano, mes, int(dia))
                            
                            transacoes.append({
                                'data': data_gasto.isoformat(),
                                'descricao': descricao,
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

        nome_limpo = re.sub(r'- Parcela \d+/\d+', '', g.descricao).strip()
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