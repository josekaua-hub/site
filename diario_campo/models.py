from decimal import Decimal

from django.db import models


class Campo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    # Conversão padrão: quantos kg tem uma saca neste campo/cultura
    saca_em_kg = models.DecimalField(max_digits=7, decimal_places=2, default=50.00, help_text='Quantos kg tem uma saca (padrão)')
    # Custos fixos padrão por campo (podem ser sobrescritos no registro)
    custo_aluguel_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    custo_manutencao_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nome


class Registro(models.Model):
    campo = models.ForeignKey(Campo, related_name='registros', on_delete=models.CASCADE)
    data = models.DateField()
    titulo = models.CharField(max_length=200)
    detalhe = models.TextField(blank=True)

    TIPO_ATIVIDADE_CHOICES = [
        ('preparo_solo', 'Preparo do Solo'),
        ('plantio', 'Plantio'),
        ('adubacao', 'Adubação'),
        ('irrigacao', 'Irrigação'),
        ('capina', 'Capina / Controle de Mato'),
        ('controle_pragas_doencas', 'Controle de Pragas e Doenças'),
        ('energia_combustivel', 'Energia / Combustível'),
        ('transporte_embalagem', 'Transporte / Embalagem'),
        ('colheita', 'Colheita'),
    ]

    tipo_atividade = models.CharField(
        max_length=30,
        choices=TIPO_ATIVIDADE_CHOICES,
        blank=True,
        default=''
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text='Número de eventos ou escala')
    quantidade_unidade = models.CharField(max_length=50, blank=True, default='', help_text='Unidade da quantidade')
    recurso_tipo = models.CharField(max_length=50, blank=True, default='', help_text='Recurso utilizado, se aplicável')
    medida_tipo = models.CharField(max_length=50, blank=True, default='', help_text='Período ou medida de consumo, se aplicável')
    valor_gasto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text='Custo total da atividade')

    quantidade_produzida = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_sementes = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_adubo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_defensivos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_agua = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_mao_obra = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_energia = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_colheita = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_transporte = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_aluguel = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    custo_manutencao = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    ciclos_por_ano = models.PositiveSmallIntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f"{self.data} — {self.titulo}"

    @property
    def custos_variaveis(self):
        custos = sum([
            self.custo_sementes,
            self.custo_adubo,
            self.custo_defensivos,
            self.custo_agua,
            self.custo_mao_obra,
            self.custo_energia,
            self.custo_colheita,
            self.custo_transporte,
        ], Decimal('0.00'))
        if self.tipo_atividade == 'colheita':
            return custos
        if custos == Decimal('0.00') and self.valor_gasto:
            return self.valor_gasto
        return custos

    @property
    def custos_fixos(self):
        return self.custo_aluguel + self.custo_manutencao

    @property
    def custo_total_ciclo(self):
        return self.custos_variaveis + self.custos_fixos

    @property
    def receita_total(self):
        return self.quantidade_produzida * self.preco_unitario

    @property
    def lucro_total(self):
        return self.receita_total - self.custo_total_ciclo

