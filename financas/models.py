from django.db import models 


class Pessoa(models.Model):
    nome = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    TIPO_ESSENCIAL = 'E'
    TIPO_NAO_ESSENCIAL = 'N'
    TIPO_CHOICES = [
        (TIPO_ESSENCIAL, 'Essencial'),
        (TIPO_NAO_ESSENCIAL, 'Não essencial'),
    ]

    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default=TIPO_NAO_ESSENCIAL)
    limite_mensal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

# class Categoria(models.Model):
#     TIPO_ESSENCIAL = 'E'
#     TIPO_NAO_ESSENCIAL = 'N'
#     TIPO_CHOICES = [
#         (TIPO_ESSENCIAL, 'Essencial'),
#         (TIPO_NAO_ESSENCIAL, 'Não essencial'),
#     ]

#     nome = models.CharField(max_length=50)
#     tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default=TIPO_NAO_ESSENCIAL)
#     limite_mensal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     ativo = models.BooleanField(default=True)

#     class Meta:
#         verbose_name = "Categoria"
#         verbose_name_plural = "Categorias"
#         ordering = ['nome']

#     def __str__(self):
#         return f"{self.nome} ({self.get_tipo_display()})"
#     return f"{self.nome} ({self.get_tipo_display()})"


class FormaPagamento(models.Model):
    nome = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Forma de Pagamento"
        verbose_name_plural = "Formas de Pagamento"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Mes(models.Model):
    ano = models.IntegerField()
    mes = models.IntegerField()
    fechado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Mês"
        verbose_name_plural = "Meses"
        ordering = ['-ano', '-mes']
        constraints = [
            models.UniqueConstraint(fields=['ano', 'mes'], name='unique_mes_ano')
        ]

    def __str__(self):
        meses_nome = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return f"{meses_nome[self.mes]}/{self.ano}"


class Receita(models.Model):
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='receitas')
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name='receitas')

    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
        ordering = ['-data']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

class Cartao(models.Model):
    nome = models.CharField(max_length=50)
    limite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dia_vencimento = models.IntegerField(null=True, blank=True, help_text="Dia do mês que a fatura vence (ex: 3)")
    cor = models.CharField(max_length=20, default='#e9d5ff', help_text="Cor em hexadecimal para o cartão") # <-- NOVO CAMPO
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"
        ordering = ['nome']

    def __str__(self):
        return self.nome

import uuid # Coloca no topo do models.py

class Gasto(models.Model):
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE, related_name='gastos')
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='gastos')
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name='gastos')
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT, related_name='gastos')
    cartao = models.ForeignKey(Cartao, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos')
    
    # NOVOS CAMPOS
    parcela_atual = models.PositiveIntegerField(null=True, blank=True)
    total_parcelas = models.PositiveIntegerField(null=True, blank=True)
    grupo_parcelas = models.UUIDField(null=True, blank=True)

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-data']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

 
class Divida(models.Model):
    descricao = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    juros = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Ex: 14.5 para 14.5%")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Dívida"
        verbose_name_plural = "Dívidas"
        ordering = ['-juros', 'descricao'] # As com juros maiores aparecem primeiro

    def __str__(self):
        return self.descricao

    @property
    def falta_pagar(self):
        return self.valor_total - self.valor_pago


class ReservaEmergencia(models.Model):
    valor_guardado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meses_alvo = models.IntegerField(default=6, help_text="Ex: 6 meses de custo de vida")

    class Meta:
        verbose_name = "Reserva de Emergência"
        verbose_name_plural = "Reservas de Emergência"

    def __str__(self):
        return f"Reserva: R$ {self.valor_guardado}"