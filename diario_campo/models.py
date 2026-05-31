from decimal import Decimal

from django.db import models


class Campo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    saca_em_kg = models.DecimalField(max_digits=7, decimal_places=2, default=50.00, help_text='Quantos kg tem uma saca (padrão)')
    custo_aluguel_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    custo_manutencao_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ciclo_ativo = models.BooleanField(default=True, help_text='Se False, o ciclo está encerrado (colheita feita)')
    numero_ciclo = models.PositiveSmallIntegerField(default=1, help_text='Número sequencial do ciclo atual')

    def __str__(self):
        return self.nome

    @property
    def has_colheita(self):
        return self.registros.filter(tipo_atividade='colheita').exists()

    @property
    def ciclo_encerrado(self):
        return not self.ciclo_ativo

    def reiniciar_ciclo(self):
        """Arquiva os registros do ciclo atual e começa um novo."""
        # Marca todos os registros do ciclo atual com o número do ciclo
        self.registros.filter(numero_ciclo=self.numero_ciclo).update(arquivado=True)
        self.numero_ciclo += 1
        self.ciclo_ativo = True
        self.save(update_fields=['numero_ciclo', 'ciclo_ativo'])

    @property
    def registros_ciclo_atual(self):
        return self.registros.filter(arquivado=False)


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

    tipo_atividade = models.CharField(max_length=30, choices=TIPO_ATIVIDADE_CHOICES, blank=True, default='')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantidade_unidade = models.CharField(max_length=50, blank=True, default='')
    recurso_tipo = models.CharField(max_length=50, blank=True, default='')
    medida_tipo = models.CharField(max_length=50, blank=True, default='')
    valor_gasto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    quantidade_produzida = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Custos detalhados (para integração com calculadora financeira)
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

    # Controle de ciclo
    numero_ciclo = models.PositiveSmallIntegerField(default=1)
    arquivado = models.BooleanField(default=False, help_text='True quando o ciclo foi encerrado e reiniciado')

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f"{self.data} — {self.titulo}"

    @property
    def custos_variaveis(self):
        custos = sum([
            self.custo_sementes, self.custo_adubo, self.custo_defensivos,
            self.custo_agua, self.custo_mao_obra, self.custo_energia,
            self.custo_colheita, self.custo_transporte,
        ], Decimal('0.00'))
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