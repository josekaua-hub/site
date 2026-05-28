from django.shortcuts import get_object_or_404, render
from django.db.models import Case, DecimalField, Exists, F, OuterRef, Q, Sum, Value, When

from diario_campo.models import Campo, Registro
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone


def financeiro(request):
    selected_campo = None
    selected_campo_id = request.GET.get('campo_id')
    
    def format_value(value, decimals=2):
        try:
            return format(float(value or 0), f'.{int(decimals)}f')
        except (TypeError, ValueError):
            return format(0.0, f'.{int(decimals)}f')

    # Anotação: campos que têm registros com quantidade_produzida > 0
    campos = Campo.objects.annotate(
        has_colheita=Exists(Registro.objects.filter(
            campo=OuterRef('pk'), 
            tipo_atividade='colheita',
            quantidade_produzida__gt=0
        ))
    ).order_by('nome')
    
    prefill = {}
    total_valor = 0
    total_colheita_quantity = 0
    selected_campo_has_colheita = False
    show_colheita_warning = False

    if selected_campo_id:
        selected_campo = get_object_or_404(Campo, id=selected_campo_id)
        registros = Registro.objects.filter(campo=selected_campo)
        selected_campo_has_colheita = registros.filter(
            tipo_atividade='colheita',
            quantidade_produzida__gt=0
        ).exists()

        # Compute aggregates from registros even if there is no colheita
        registros_existem = registros.exists()
        ultimo_registro = registros.order_by('-data').first() if registros_existem else None

        if registros_existem:
            if not selected_campo_has_colheita:
                show_colheita_warning = True
            # Prefer specific cost fields when available, otherwise fall back to valor_gasto per activity
            specific_sums = registros.aggregate(
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

            valor_por_atividade = registros.aggregate(
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
            custoColheita = float(specific_sums.get('colheita_sum') or 0)
            custoTransporte = pick('transporte_sum', 'valor_transporte')

            # Aluguel e manutenção: prefer specific sums, else 0
            custoAluguel = float(specific_sums.get('aluguel_sum') or 0)
            custoManutencao = float(specific_sums.get('manutencao_sum') or 0)

            # Preço unitário: usar do último registro de colheita (convertendo sacas->kg se necessário)
            preco_unitario = 0
            if ultimo_registro:
                try:
                    pu = float(ultimo_registro.preco_unitario or 0)
                except Exception:
                    pu = 0
                # if unit is 'saca' and campo defines saca_em_kg, convert to price per kg
                if getattr(ultimo_registro, 'quantidade_unidade', None) == 'saca' and selected_campo and getattr(selected_campo, 'saca_em_kg', None):
                    try:
                        saca_kg = float(selected_campo.saca_em_kg)
                        if saca_kg:
                            preco_unitario = pu / saca_kg
                        else:
                            preco_unitario = pu
                    except Exception:
                        preco_unitario = pu
                else:
                    preco_unitario = pu
            else:
                preco_unitario = 0

            if preco_unitario == 0 and registros.filter(tipo_atividade='colheita', preco_unitario__gt=0).exists():
                outro = registros.filter(tipo_atividade='colheita', preco_unitario__gt=0).order_by('-data').first()
                if outro:
                    try:
                        pu = float(outro.preco_unitario or 0)
                    except Exception:
                        pu = 0
                    if getattr(outro, 'quantidade_unidade', None) == 'saca' and selected_campo and getattr(selected_campo, 'saca_em_kg', None):
                        try:
                            saca_kg = float(selected_campo.saca_em_kg)
                            preco_unitario = pu / saca_kg if saca_kg else pu
                        except Exception:
                            preco_unitario = pu
                    else:
                        preco_unitario = pu

            # If still zero, try derive price as receita_total / quantidade_produzida across colheitas (convert sacas->kg)
            colheitas = registros.filter(tipo_atividade='colheita', quantidade_produzida__gt=0)
            if preco_unitario == 0 and colheitas.exists():
                total_receita = 0
                total_qtd = 0
                for r in colheitas:
                    try:
                        r_qtd = float(r.quantidade_produzida or 0)
                    except Exception:
                        r_qtd = 0
                    try:
                        r_preco = float(r.preco_unitario or 0)
                    except Exception:
                        r_preco = 0

                    # convert sacks to kg for quantity sum
                    if getattr(r, 'quantidade_unidade', None) == 'saca' and selected_campo and getattr(selected_campo, 'saca_em_kg', None):
                        try:
                            r_qtd_converted = r_qtd * float(selected_campo.saca_em_kg)
                        except Exception:
                            r_qtd_converted = r_qtd
                        # revenue in R$ remains r_qtd * r_preco (price per sack)
                        total_receita += r_qtd * r_preco
                        total_qtd += r_qtd_converted
                    else:
                        total_receita += r_qtd * r_preco
                        total_qtd += r_qtd

                try:
                    preco_unitario = float(total_receita) / float(total_qtd) if total_qtd else 0
                except Exception:
                    preco_unitario = 0

            # Final fallback: if still zero, estimate price as total custos / total quantidade de colheita
            total_colheita_quantity = 0
            if colheitas.exists():
                # sum converted quantities (saca->kg) for display and rateio
                total_q = 0
                for r in colheitas:
                    try:
                        r_q = float(r.quantidade_produzida or 0)
                    except Exception:
                        r_q = 0
                    if getattr(r, 'quantidade_unidade', None) == 'saca' and selected_campo and getattr(selected_campo, 'saca_em_kg', None):
                        try:
                            r_q = r_q * float(selected_campo.saca_em_kg)
                        except Exception:
                            pass
                    total_q += r_q
                total_colheita_quantity = float(total_q)

            if preco_unitario == 0 and total_colheita_quantity:
                total_valor_est = (
                    custoSementes + custoAdubo + custoDefensivos + custoAgua +
                    custoMaoObra + custoEnergia + custoColheita + custoTransporte +
                    custoAluguel + custoManutencao
                )
                try:
                    preco_unitario = float(total_valor_est) / float(total_colheita_quantity)
                except Exception:
                    preco_unitario = 0

            prefill = {
                'custoSementes': format_value(custoSementes),
                'custoAdubo': format_value(custoAdubo),
                'custoDefensivos': format_value(custoDefensivos),
                'custoAgua': format_value(custoAgua),
                'custoMaoObra': format_value(custoMaoObra),
                'custoEnergia': format_value(custoEnergia),
                'custoColheita': format_value(custoColheita),
                'custoTransporte': format_value(custoTransporte),
                'custoAluguel': format_value(custoAluguel),
                'custoManutencao': format_value(custoManutencao),
                'ciclosPorAno': str(int(ultimo_registro.ciclos_por_ano)) if ultimo_registro else '1',
                'qtdProduzida': format_value(
                    (float(ultimo_registro.quantidade_produzida) * float(selected_campo.saca_em_kg)) if (ultimo_registro and ultimo_registro.tipo_atividade=='colheita' and getattr(ultimo_registro, 'quantidade_unidade', None) == 'saca' and getattr(selected_campo, 'saca_em_kg', None)) else (float(ultimo_registro.quantidade_produzida) if (ultimo_registro and ultimo_registro.tipo_atividade=='colheita') else 0)
                ,),
                'precoUnitario': format_value(preco_unitario),
            }

            total_valor = (
                custoSementes + custoAdubo + custoDefensivos +
                custoAgua + custoMaoObra + custoEnergia +
                custoColheita + custoTransporte + custoAluguel +
                custoManutencao
            )
            # total_colheita_quantity already computed when needed; keep for template
            total_colheita_quantity = float(registros.filter(tipo_atividade='colheita').aggregate(total_q=Sum('quantidade_produzida')).get('total_q') or 0)
        else:
            show_colheita_warning = True

    return render(request, 'financeiro.html', {
        'campos': campos,
        'selected_campo': selected_campo,
        'selected_campo_id': selected_campo_id,
        'prefill': prefill,
        'total_valor': total_valor,
        'total_colheita_quantity': total_colheita_quantity,
        'selected_campo_has_colheita': selected_campo_has_colheita,
        'show_colheita_warning': show_colheita_warning,
    })


def salvar_fixos(request):
    if request.method != 'POST':
        return redirect(reverse('financeiro:financeiro'))

    campo_id = request.POST.get('campo_id')
    if not campo_id:
        return redirect(reverse('financeiro:financeiro'))

    try:
        campo = Campo.objects.get(id=campo_id)
    except Campo.DoesNotExist:
        return redirect(reverse('financeiro:financeiro'))

    # Parse values with support for comma or dot decimal separators and thousands separators
    def to_decimal(name):
        value = request.POST.get(name) or 0
        if isinstance(value, str):
            value = value.strip()
            if ',' in value and '.' in value:
                value = value.replace('.', '')
            value = value.replace(',', '.')
        try:
            return float(value)
        except Exception:
            return 0

    aluguel = to_decimal('custoAluguel')
    manutencao = to_decimal('custoManutencao')

    today = timezone.now().date()
    created = False
    if aluguel and aluguel > 0:
        Registro.objects.create(
            campo=campo,
            data=today,
            titulo='Aluguel (adicionado via Financeiro)',
            tipo_atividade='',
            detalhe='Registro criado a partir da calculadora financeira',
            valor_gasto=aluguel,
            custo_aluguel=aluguel,
        )
        created = True

    if manutencao and manutencao > 0:
        Registro.objects.create(
            campo=campo,
            data=today,
            titulo='Manutenção (adicionado via Financeiro)',
            tipo_atividade='',
            detalhe='Registro criado a partir da calculadora financeira',
            valor_gasto=manutencao,
            custo_manutencao=manutencao,
        )
        created = True

    # Redirect back to financeiro with campo selected
    url = reverse('financeiro:financeiro') + f'?campo_id={campo.id}'
    return redirect(url)
