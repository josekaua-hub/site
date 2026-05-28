from diario_campo.models import Campo, Registro
from django.db.models import Case, When, Sum, F, Value, DecimalField

for c in Campo.objects.all():
    regs = Registro.objects.filter(campo=c)
    specific_sums = regs.aggregate(
        sementes_sum=Sum('custo_sementes'),
        adubo_sum=Sum('custo_adubo'),
        defensivos_sum=Sum('custo_defensivos'),
        agua_sum=Sum('custo_agua'),
        mao_obra_sum=Sum('custo_mao_obra'),
        energia_sum=Sum('custo_energia'),
        colheita_sum=Sum('custo_colheita'),
        transporte_sum=Sum('custo_transporte'),
        aluguel_sum=Sum('custo_aluguel'),
        manutencao_sum=Sum('custo_manutencao'),
    )

    valor_por_atividade = regs.aggregate(
        valor_plantio=Sum(Case(When(tipo_atividade='plantio', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_adubacao=Sum(Case(When(tipo_atividade='adubacao', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_defensivos=Sum(Case(When(tipo_atividade='controle_pragas_doencas', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_irrigacao=Sum(Case(When(tipo_atividade='irrigacao', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_mao_obra=Sum(Case(When(tipo_atividade__in=['preparo_solo', 'capina'], then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_energia=Sum(Case(When(tipo_atividade='energia_combustivel', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_colheita=Sum(Case(When(tipo_atividade='colheita', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
        valor_transporte=Sum(Case(When(tipo_atividade='transporte_embalagem', then=F('valor_gasto')), default=Value(0), output_field=DecimalField())),
    )

    def pick(specific_key, valor_key):
        specific = specific_sums.get(specific_key) or 0
        if specific and specific != 0:
            return float(specific)
        return float(valor_por_atividade.get(valor_key) or 0)

    custoSementes = pick('sementes_sum', 'valor_plantio')
    custoAdubo = pick('adubo_sum', 'valor_adubacao')
    custoDefensivos = pick('defensivos_sum', 'valor_defensivos')
    custoAgua = pick('agua_sum', 'valor_irrigacao')
    custoMaoObra = pick('mao_obra_sum', 'valor_mao_obra')
    custoEnergia = pick('energia_sum', 'valor_energia')
    custoColheita = pick('colheita_sum', 'valor_colheita')
    custoTransporte = pick('transporte_sum', 'valor_transporte')
    custoAluguel = float(specific_sums.get('aluguel_sum') or 0)
    custoManutencao = float(specific_sums.get('manutencao_sum') or 0)

    ultimo_registro = regs.filter(tipo_atividade='colheita', quantidade_produzida__gt=0).order_by('-data').first()
    preco_unitario = float(ultimo_registro.preco_unitario or 0) if ultimo_registro else 0
    if preco_unitario == 0 and ultimo_registro:
        outro = regs.filter(tipo_atividade='colheita', preco_unitario__gt=0).order_by('-data').first()
        if outro:
            preco_unitario = float(outro.preco_unitario)

    prefill = {
        'campo': c.nome,
        'custoSementes': custoSementes,
        'custoAdubo': custoAdubo,
        'custoDefensivos': custoDefensivos,
        'custoAgua': custoAgua,
        'custoMaoObra': custoMaoObra,
        'custoEnergia': custoEnergia,
        'custoColheita': custoColheita,
        'custoTransporte': custoTransporte,
        'custoAluguel': custoAluguel,
        'custoManutencao': custoManutencao,
        'precoUnitario': preco_unitario,
    }

    print(prefill)
