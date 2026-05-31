from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Exists, OuterRef

from diario_campo.models import Campo, Registro


def financeiro(request):
    campos = Campo.objects.annotate(
        colheita_anotada=Exists(
            Registro.objects.filter(
                campo=OuterRef('pk'),
                tipo_atividade='colheita',
                quantidade_produzida__gt=0,
            )
        )
    ).order_by('nome')

    selected_campo = None
    prefill = {}
    resumo = {}
    registros_lista = []
    show_colheita_warning = False

    campo_id = request.GET.get('campo_id')
    if campo_id:
        selected_campo = get_object_or_404(Campo, id=campo_id)
        registros = Registro.objects.filter(campo=selected_campo).order_by('data')

        # Mapa: tipo de atividade → categoria de custo na calculadora
        TIPO_PARA_CUSTO = {
            'preparo_solo':            'mao_obra',
            'plantio':                 'sementes',
            'adubacao':                'adubo',
            'irrigacao':               'agua',
            'capina':                  'mao_obra',
            'controle_pragas_doencas': 'defensivos',
            'energia_combustivel':     'energia',
            'transporte_embalagem':    'transporte',
        }

        # Acumuladores — só gastos (sem colheita)
        custo_sementes = custo_adubo = custo_defensivos = custo_agua = 0.0
        custo_mao_obra = custo_energia = custo_transporte = 0.0
        # aluguel e manutenção vêm dos padrões do Campo, não dos registros individuais
        # (cada registro copia o padrão, o que causava multiplicação errada)
        total_gastos = 0.0

        gastos_qs = registros.exclude(tipo_atividade='colheita')

        for r in gastos_qs:
            vg = float(r.valor_gasto or 0)
            total_gastos += vg

            # Verifica se o registro tem custos detalhados preenchidos
            # (ignora custo_aluguel e custo_manutencao aqui — virão do campo)
            cs  = float(r.custo_sementes or 0)
            ca  = float(r.custo_adubo or 0)
            cd  = float(r.custo_defensivos or 0)
            cag = float(r.custo_agua or 0)
            cmo = float(r.custo_mao_obra or 0)
            ce  = float(r.custo_energia or 0)
            cc  = float(r.custo_colheita or 0)   # custo de processamento pós-colheita
            ct  = float(r.custo_transporte or 0)

            soma_detalhada = cs + ca + cd + cag + cmo + ce + cc + ct

            if soma_detalhada > 0:
                # Usa os campos detalhados do registro
                custo_sementes   += cs
                custo_adubo      += ca
                custo_defensivos += cd
                custo_agua       += cag
                custo_mao_obra   += cmo
                custo_energia    += ce
                # cc (custo_colheita = processamento) não é somado aqui porque
                # geralmente é zero nos registros de gasto do diário
                custo_transporte += ct
            else:
                # Fallback: distribui valor_gasto pela categoria do tipo de atividade
                dest = TIPO_PARA_CUSTO.get(r.tipo_atividade, 'mao_obra')
                if dest == 'sementes':    custo_sementes   += vg
                elif dest == 'adubo':     custo_adubo      += vg
                elif dest == 'defensivos':custo_defensivos += vg
                elif dest == 'agua':      custo_agua       += vg
                elif dest == 'mao_obra':  custo_mao_obra   += vg
                elif dest == 'energia':   custo_energia    += vg
                elif dest == 'transporte':custo_transporte += vg

        # Aluguel e manutenção: usa os padrões do campo (evita multiplicação)
        custo_aluguel    = float(selected_campo.custo_aluguel_padrao or 0)
        custo_manutencao = float(selected_campo.custo_manutencao_padrao or 0)

        # Receita: vem do registro de colheita
        colheita_reg = registros.filter(tipo_atividade='colheita').order_by('-data').first()
        qtd_produzida  = 0.0
        preco_unitario = 0.0
        total_receita  = 0.0
        unidade_colheita = '—'

        if colheita_reg:
            qtd_produzida    = float(colheita_reg.quantidade_produzida or 0)
            preco_unitario   = float(colheita_reg.preco_unitario or 0)
            total_receita    = qtd_produzida * preco_unitario
            unidade_colheita = colheita_reg.quantidade_unidade or '—'
        else:
            show_colheita_warning = True

        saldo = total_receita - total_gastos

        resumo = {
            'total_gastos':  total_gastos,
            'total_receita': total_receita,
            'saldo':         saldo,
            'qtd_produzida': qtd_produzida,
            'unidade':       unidade_colheita,
            'num_registros': registros.count(),
        }

        prefill = {
            'qtdProduzida':    f'{qtd_produzida:.2f}',
            'precoUnitario':   f'{preco_unitario:.2f}',
            'custoSementes':   f'{custo_sementes:.2f}',
            'custoAdubo':      f'{custo_adubo:.2f}',
            'custoDefensivos': f'{custo_defensivos:.2f}',
            'custoAgua':       f'{custo_agua:.2f}',
            'custoMaoObra':    f'{custo_mao_obra:.2f}',
            'custoEnergia':    f'{custo_energia:.2f}',
            'custoColheita':   '0.00',   # processamento pós-colheita: preenchimento manual
            'custoTransporte': f'{custo_transporte:.2f}',
            'custoAluguel':    f'{custo_aluguel:.2f}',
            'custoManutencao': f'{custo_manutencao:.2f}',
            'ciclosPorAno':    '1',
        }

        ICONES = {
            'preparo_solo': '🚜', 'plantio': '🌱', 'adubacao': '🧪',
            'irrigacao': '💧', 'capina': '🌿', 'controle_pragas_doencas': '🐛',
            'energia_combustivel': '⛽', 'transporte_embalagem': '🚚',
            'colheita': '🌾',
        }
        for r in registros:
            registros_lista.append({
                'icone':      ICONES.get(r.tipo_atividade, '📌'),
                'titulo':     r.titulo,
                'tipo':       r.get_tipo_atividade_display(),
                'data':       r.data.strftime('%d/%m/%Y'),
                'valor':      float(r.receita_total if r.tipo_atividade == 'colheita' else r.valor_gasto),
                'eh_receita': r.tipo_atividade == 'colheita',
                'unidade':    r.quantidade_unidade or '',
                'quantidade': float(r.quantidade_produzida if r.tipo_atividade == 'colheita' else r.quantidade),
            })

    return render(request, 'financeiro.html', {
        'campos':                campos,
        'selected_campo':        selected_campo,
        'prefill':               prefill,
        'resumo':                resumo,
        'registros_lista':       registros_lista,
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

    def to_float(name):
        try:
            return float(request.POST.get(name) or 0)
        except Exception:
            return 0.0

    from django.utils import timezone
    today = timezone.now().date()

    aluguel    = to_float('custoAluguel')
    manutencao = to_float('custoManutencao')

    # Atualiza os padrões do campo em vez de criar registros duplicados
    campo.custo_aluguel_padrao    = aluguel
    campo.custo_manutencao_padrao = manutencao
    campo.save()

    return redirect(reverse('financeiro:financeiro') + f'?campo_id={campo.id}')
