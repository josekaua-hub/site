from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Exists, OuterRef

from diario_campo.models import Campo, Registro


def financeiro(request):
    # Campos só aparecem para usuários autenticados
    if request.user.is_authenticated:
        campos = Campo.objects.filter(usuario=request.user).annotate(
            colheita_anotada=Exists(
                Registro.objects.filter(
                    campo=OuterRef('pk'),
                    tipo_atividade='colheita',
                    quantidade_produzida__gt=0,
                )
            )
        ).order_by('nome')
    else:
        campos = None

    selected_campo = None
    prefill = {}
    resumo = {}
    registros_lista = []
    show_colheita_warning = False
    ciclos_disponiveis = []
    ciclo_selecionado = None
    ciclo_atual = None

    campo_id = request.GET.get('campo_id')
    if campo_id and request.user.is_authenticated:
        selected_campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
        ciclo_atual = selected_campo.numero_ciclo

        # Ciclos que possuem registros (separa o cálculo por ciclo)
        ciclos_disponiveis = sorted(set(
            Registro.objects.filter(campo=selected_campo)
                            .values_list('numero_ciclo', flat=True)
        ))
        if ciclo_atual not in ciclos_disponiveis:
            ciclos_disponiveis.append(ciclo_atual)
            ciclos_disponiveis.sort()

        # Ciclo pedido na URL (?ciclo=N); padrão = ciclo atual do campo
        try:
            ciclo_selecionado = int(request.GET.get('ciclo', ciclo_atual))
        except (TypeError, ValueError):
            ciclo_selecionado = ciclo_atual
        if ciclo_selecionado not in ciclos_disponiveis:
            ciclo_selecionado = ciclo_atual

        # Apenas os registros do ciclo selecionado deste campo
        registros = Registro.objects.filter(
            campo=selected_campo, numero_ciclo=ciclo_selecionado
        ).order_by('data')

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
        total_gastos = 0.0

        gastos_qs = registros.exclude(tipo_atividade='colheita')

        for r in gastos_qs:
            vg = float(r.valor_gasto or 0)
            total_gastos += vg

            cs  = float(r.custo_sementes or 0)
            ca  = float(r.custo_adubo or 0)
            cd  = float(r.custo_defensivos or 0)
            cag = float(r.custo_agua or 0)
            cmo = float(r.custo_mao_obra or 0)
            ce  = float(r.custo_energia or 0)
            cc  = float(r.custo_colheita or 0)
            ct  = float(r.custo_transporte or 0)

            soma_detalhada = cs + ca + cd + cag + cmo + ce + cc + ct

            if soma_detalhada > 0:
                custo_sementes   += cs
                custo_adubo      += ca
                custo_defensivos += cd
                custo_agua       += cag
                custo_mao_obra   += cmo
                custo_energia    += ce
                custo_transporte += ct
            else:
                dest = TIPO_PARA_CUSTO.get(r.tipo_atividade, 'mao_obra')
                if dest == 'sementes':    custo_sementes   += vg
                elif dest == 'adubo':     custo_adubo      += vg
                elif dest == 'defensivos':custo_defensivos += vg
                elif dest == 'agua':      custo_agua       += vg
                elif dest == 'mao_obra':  custo_mao_obra   += vg
                elif dest == 'energia':   custo_energia    += vg
                elif dest == 'transporte':custo_transporte += vg

        custo_aluguel    = float(selected_campo.custo_aluguel_padrao or 0)
        custo_manutencao = float(selected_campo.custo_manutencao_padrao or 0)

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
            'ciclo':         ciclo_selecionado,
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
            'custoColheita':   '0.00',
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
        'ciclos_disponiveis':    ciclos_disponiveis,
        'ciclo_selecionado':     ciclo_selecionado,
        'ciclo_atual':           ciclo_atual,
    })


@login_required(login_url="login")
def salvar_fixos(request):
    if request.method != 'POST':
        return redirect(reverse('financeiro:financeiro'))

    campo_id = request.POST.get('campo_id')
    if not campo_id:
        return redirect(reverse('financeiro:financeiro'))

    try:
        campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    except Campo.DoesNotExist:
        return redirect(reverse('financeiro:financeiro'))

    def to_float(name):
        try:
            return float(request.POST.get(name) or 0)
        except Exception:
            return 0.0

    aluguel    = to_float('custoAluguel')
    manutencao = to_float('custoManutencao')

    campo.custo_aluguel_padrao    = aluguel
    campo.custo_manutencao_padrao = manutencao
    campo.save()

    return redirect(reverse('financeiro:financeiro') + f'?campo_id={campo.id}')
