from django import forms
from .models import Pessoa, Categoria, FormaPagamento, Mes, Receita, Gasto, Cartao, Divida, ReservaEmergencia
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from .models import Perfil

MESES_CHOICES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
    (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]

class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ['nome', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da pessoa'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'tipo', 'limite_mensal', 'cor', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mercado, Luz, Lazer'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'limite_mensal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Deixe vazio se não tiver limite'}),
            'cor': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color', 'title': 'Escolha a cor da categoria'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# class CategoriaForm(forms.ModelForm):
#     class Meta:
#         model = Categoria
#         fields = ['nome', 'tipo', 'limite_mensal', 'ativo']
#         widgets = {
#             'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mercado, Luz, Lazer'}),
#             'tipo': forms.Select(attrs={'class': 'form-select'}),
#             'limite_mensal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Deixe vazio se não tiver limite'}),
#             'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = ['nome', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Pix, Débito, Dinheiro'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MesForm(forms.ModelForm):
    mes = forms.ChoiceField(choices=MESES_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Mes
        fields = ['ano', 'mes']
        widgets = {
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2026'}),
        }

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['descricao', 'valor', 'data', 'pessoa']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Salário, Freela, Venda'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pessoa': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['data'].initial = date.today()
        self.fields['pessoa'].queryset = Pessoa.objects.filter(ativo=True)

class GastoForm(forms.ModelForm):
    parcela_atual = forms.IntegerField(
        required=False, min_value=1, initial=1, label="Parcela Atual",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    total_parcelas = forms.IntegerField(
        required=False, min_value=1, initial=1, label="Total de Parcelas",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )

    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'data', 'categoria', 'pessoa', 'forma_pagamento', 'cartao']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Compra do mês, TV Nova'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Valor da Parcela / Total'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'pessoa': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'cartao': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['data'].initial = date.today()
        
        self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)
        self.fields['pessoa'].queryset = Pessoa.objects.filter(ativo=True)
        self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(ativo=True)
        self.fields['cartao'].queryset = Cartao.objects.filter(ativo=True)
        
        self.fields['cartao'].required = False
        self.fields['cartao'].empty_label = "Nenhum / Não é cartão"

# class GastoForm(forms.ModelForm):
#     # Novos campos para o parcelamento inteligente
#     parcela_atual = forms.IntegerField(
#         required=False, min_value=1, initial=1, label="Parcela Atual",
#         widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
#     )
#     total_parcelas = forms.IntegerField(
#         required=False, min_value=1, initial=1, label="Total de Parcelas",
#         widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
#     )

#     class Meta:
#         model = Gasto
#         fields = ['descricao', 'valor', 'data', 'categoria', 'pessoa', 'forma_pagamento', 'cartao']
#         widgets = {
#             'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Notebook, Geladeira'}),
#             'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Valor TOTAL'}),
#             'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'categoria': forms.Select(attrs={'class': 'form-select'}),
#             'pessoa': forms.Select(attrs={'class': 'form-select'}),
#             'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
#             'cartao': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not self.instance.pk:
#             self.fields['data'].initial = date.today()
        
#         self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)
#         self.fields['pessoa'].queryset = Pessoa.objects.filter(ativo=True)
#         self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(ativo=True)
#         self.fields['cartao'].queryset = Cartao.objects.filter(ativo=True)
        
#         self.fields['cartao'].required = False
#         self.fields['cartao'].empty_label = "Nenhum / Não é cartão"

# class GastoForm(forms.ModelForm):
#     # Campo extra que NÃO existe no banco, só na tela
#     parcelas = forms.IntegerField(
#         required=False, 
#         min_value=1, 
#         initial=1, 
#         label="Parcelas",
#         widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
#     )

#     class Meta:
#         model = Gasto
#         fields = ['descricao', 'valor', 'data', 'categoria', 'pessoa', 'forma_pagamento', 'cartao']
#         widgets = {
#             'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Notebook, Geladeira'}),
#             'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Valor TOTAL da compra'}),
#             'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'categoria': forms.Select(attrs={'class': 'form-select'}),
#             'pessoa': forms.Select(attrs={'class': 'form-select'}),
#             'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
#             'cartao': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not self.instance.pk:
#             self.fields['data'].initial = date.today()
        
#         self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)
#         self.fields['pessoa'].queryset = Pessoa.objects.filter(ativo=True)
#         self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(ativo=True)
#         self.fields['cartao'].queryset = Cartao.objects.filter(ativo=True)
        
#         self.fields['cartao'].required = False
#         self.fields['cartao'].empty_label = "Nenhum / Não é cartão"

# class GastoForm(forms.ModelForm):
#     class Meta:
#         model = Gasto
#         fields = ['descricao', 'valor', 'data', 'categoria', 'pessoa', 'forma_pagamento', 'cartao']
#         widgets = {
#             'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Compra do mês, Luz, Farmácia'}),
#             'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
#             'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'categoria': forms.Select(attrs={'class': 'form-select'}),
#             'pessoa': forms.Select(attrs={'class': 'form-select'}),
#             'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
#             'cartao': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not self.instance.pk:
#             self.fields['data'].initial = date.today()
        
#         # Filtra só o que tá ativo nos dropdowns
#         self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)
#         self.fields['pessoa'].queryset = Pessoa.objects.filter(ativo=True)
#         self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(ativo=True)
#         self.fields['cartao'].queryset = Cartao.objects.filter(ativo=True)
        
#         # Adiciona a opção "Nenhum" pro cartão não ser obrigatório
#         self.fields['cartao'].required = False
#         self.fields['cartao'].empty_label = "Nenhum / Não é cartão"

# class GastoForm(forms.ModelForm):
#     class Meta:
#         model = Gasto
#         fields = ['descricao', 'valor', 'data', 'categoria', 'pessoa', 'forma_pagamento', 'cartao']
#         widgets = {
#             'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Compra do mês, Luz, Farmácia'}),
#             'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
#             'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'categoria': forms.Select(attrs={'class': 'form-select'}),
#             'pessoa': forms.Select(attrs={'class': 'form-select'}),
#             'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
#             'cartao': forms.Select(attrs={'class': 'form-select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not self.instance.pk:
#             self.fields['data'].initial = date.today()
#         self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)
#         self.fields['pessoa'].queryset = Pessoa.objects.filter(ativo=True)
#         self.fields['forma_pagamento'].queryset = FormaPagamento.objects.filter(ativo=True)
#         self.fields['cartao'].queryset = Cartao.objects.filter(ativo=True)

class CartaoForm(forms.ModelForm):
    class Meta:
        model = Cartao
        fields = ['nome', 'limite', 'dia_vencimento', 'cor', 'ativo'] # <-- 'cor' adicionado
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Nubank Isaias'}),
            'limite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'dia_vencimento': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '31', 'placeholder': 'Ex: 3'}),
            'cor': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color', 'title': 'Escolha a cor do cartão'}), # <-- TYPE COLOR
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DividaForm(forms.ModelForm):
    class Meta:
        model = Divida
        fields = ['descricao', 'valor_total', 'valor_pago', 'juros', 'ativo']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Empréstimo Banco, Cartão Rotativo'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'juros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 14.5'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = ReservaEmergencia
        fields = ['valor_guardado', 'meses_alvo']
        widgets = {
            'valor_guardado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'meses_alvo': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']
        widgets = {
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AlterarSenhaForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Senha Atual")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Nova Senha")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar Nova Senha")