from diario_campo.models import Campo, Registro
from django.db.models import Case, When, Sum, F, Value, DecimalField

c = Campo.objects.get(nome='campo1')
regs = Registro.objects.filter(campo=c)

print('Total registros:', regs.count())
print('Registros:')
for r in regs:
    print('- ', r.id, r.tipo_atividade, r.valor_gasto, r.custo_sementes, r.custo_adubo)

print('\nSomas específicas:')
sums = regs.aggregate(
    sementes_sum=Sum('custo_sementes'),
    adubo_sum=Sum('custo_adubo'),
    defensivos_sum=Sum('custo_defensivos'),
    agua_sum=Sum('custo_agua'),
    mao_obra_sum=Sum('custo_mao_obra'),
    energia_sum=Sum('custo_energia'),
    colheita_sum=Sum('custo_colheita'),
    transporte_sum=Sum('custo_transporte'),
)
print(sums)

print('\nValor por atividade:')
valor_activity = regs.aggregate(
    valor_plantio=Sum(Case(When(tipo_atividade='plantio', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_adubacao=Sum(Case(When(tipo_atividade='adubacao', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_defensivos=Sum(Case(When(tipo_atividade='controle_pragas_doencas', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_irrigacao=Sum(Case(When(tipo_atividade='irrigacao', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_mao_obra=Sum(Case(When(tipo_atividade__in=['preparo_solo', 'capina'], then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_energia=Sum(Case(When(tipo_atividade='energia_combustivel', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_colheita=Sum(Case(When(tipo_atividade='colheita', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    valor_transporte=Sum(Case(When(tipo_atividade='transporte_embalagem', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
)
print(valor_activity)
