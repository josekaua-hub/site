from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from .models import Campo, Registro


# ─── helpers ────────────────────────────────────────────────────────────────

TIPOS_GASTO   = {'preparo_solo', 'plantio', 'adubacao', 'irrigacao',
                 'capina', 'controle_pragas_doencas', 'energia_combustivel',
                 'transporte_embalagem', 'pos_colheita'}
TIPOS_RECEITA = {'colheita'}
TIPOS_ONE_TIME = {'preparo_solo', 'plantio', 'colheita'}
# Gastos cujo valor informado é POR UNIDADE (total = quantidade × valor)
TIPOS_COM_QUANTIDADE = {'adubacao', 'irrigacao', 'capina', 'controle_pragas_doencas',
                        'energia_combustivel', 'transporte_embalagem', 'pos_colheita'}

ATIVIDADE_INFO = [
    {'value': 'preparo_solo',            'label': 'Preparo do Solo',             'tipo': 'gasto',   'one_time': True},
    {'value': 'plantio',                 'label': 'Plantio',                     'tipo': 'gasto',   'one_time': True},
    {'value': 'adubacao',                'label': 'Adubação',                    'tipo': 'gasto',   'one_time': False},
    {'value': 'irrigacao',               'label': 'Irrigação',                   'tipo': 'gasto',   'one_time': False},
    {'value': 'capina',                  'label': 'Capina / Controle de Mato',   'tipo': 'gasto',   'one_time': False},
    {'value': 'controle_pragas_doencas', 'label': 'Controle de Pragas e Doenças','tipo': 'gasto',   'one_time': False},
    {'value': 'energia_combustivel',     'label': 'Energia / Combustível',       'tipo': 'gasto',   'one_time': False},
    {'value': 'transporte_embalagem',    'label': 'Transporte / Embalagem',      'tipo': 'gasto',   'one_time': False},
    {'value': 'colheita',                'label': 'Colheita',                    'tipo': 'receita', 'one_time': True},
    {'value': 'pos_colheita',            'label': 'Pós-colheita / Beneficiamento','tipo': 'gasto',   'one_time': False},
]


def _clean_dec(val, default='0'):
    try:
        return str(Decimal(str(val).replace(',', '.').strip()))
    except (InvalidOperation, AttributeError):
        return default


def _build_pdf_table(registros):
    """Monta a tabela de registros para PDF."""
    header = ['Data', 'Tipo', 'Título', 'Qtd', 'Unidade', 'Valor Gasto', 'Qtd Produzida', 'Preço Unit.']
    rows = [header]
    for r in registros:
        rows.append([
            r.data.strftime('%d/%m/%Y'),
            r.get_tipo_atividade_display() if r.tipo_atividade else '—',
            r.titulo,
            str(r.quantidade),
            r.quantidade_unidade or '—',
            f"R$ {r.valor_gasto:.2f}",
            str(r.quantidade_produzida) if r.tipo_atividade == 'colheita' else '—',
            f"R$ {r.preco_unitario:.2f}" if r.tipo_atividade == 'colheita' else '—',
        ])
    return rows


def _render_pdf(response, campo, registros, numero_ciclo=None):
    """Gera PDF de registros e escreve em response."""
    if numero_ciclo is None:
        numero_ciclo = campo.numero_ciclo
    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=14, spaceAfter=6)
    sub_style   = ParagraphStyle('sub',   parent=styles['Normal'], fontSize=9, textColor=colors.grey, spaceAfter=12)

    # Calcular saldo
    total_gastos  = sum(r.valor_gasto   for r in registros if r.tipo_atividade not in TIPOS_RECEITA)
    total_receita = sum(r.receita_total for r in registros if r.tipo_atividade in TIPOS_RECEITA)
    saldo         = total_receita - total_gastos

    elements = [
        Paragraph(f"Diário de Campo — {campo.nome}", title_style),
        Paragraph(f"Ciclo {numero_ciclo}  |  Registros: {len(registros)}  |  "
                  f"Gastos: R$ {total_gastos:.2f}  |  Receita: R$ {total_receita:.2f}  |  "
                  f"Saldo: R$ {saldo:.2f}", sub_style),
    ]

    if registros:
        rows = _build_pdf_table(registros)
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 8),
            ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7f3')]),
            ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Nenhum registro neste ciclo.", styles['Normal']))

    doc.build(elements)


# ─── views ──────────────────────────────────────────────────────────────────

@login_required(login_url="login")
def selecionar_campo(request):
    error_message = None
    if request.method == 'POST':
        nome = request.POST.get('nome_campo', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        if nome:
            campo, created = Campo.objects.get_or_create(
                usuario=request.user,
                nome=nome,
                defaults={'descricao': descricao}
            )
            return redirect('diario_campo_form', campo_id=campo.id)
        else:
            error_message = 'Digite um nome para o campo.'

    campos = Campo.objects.filter(usuario=request.user).order_by('nome')
    # Anotar contagem de registros ativos
    campos_data = []
    for c in campos:
        regs = c.registros_ciclo_atual
        total_gastos  = sum(r.valor_gasto   for r in regs if r.tipo_atividade not in TIPOS_RECEITA)
        total_receita = sum(r.receita_total for r in regs if r.tipo_atividade in TIPOS_RECEITA)
        ciclos = sorted(set(
            c.registros.values_list('numero_ciclo', flat=True)
        ))
        campos_data.append({
            'campo': c,
            'num_registros': regs.count(),
            'total_gastos': total_gastos,
            'total_receita': total_receita,
            'saldo': total_receita - total_gastos,
            'ciclos': ciclos,
        })
    return render(request, 'selecionar_campo.html', {
        'campos_data': campos_data,
        'error_message': error_message,
    })


@login_required(login_url="login")
def excluir_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    if request.method == 'POST':
        campo.delete()
    return redirect('diario_campo')


@login_required(login_url="login")
def excluir_registro(request, registro_id):
    registro = get_object_or_404(Registro, id=registro_id, campo__usuario=request.user)
    campo_id = registro.campo.id
    if request.method == 'POST':
        # Se era o único registro de colheita, reativa o ciclo
        campo = registro.campo
        era_colheita = registro.tipo_atividade == 'colheita'
        registro.delete()
        if era_colheita and not campo.registros.filter(tipo_atividade='colheita', arquivado=False).exists():
            campo.ciclo_ativo = True
            campo.save(update_fields=['ciclo_ativo'])
    return redirect('diario_campo_form', campo_id=campo_id)


@login_required(login_url="login")
def reiniciar_ciclo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    if request.method == 'POST':
        campo.reiniciar_ciclo()
    return redirect('diario_campo_form', campo_id=campo_id)


@login_required(login_url="login")
def diario_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    colheita_done = campo.registros.filter(tipo_atividade='colheita', arquivado=False).exists()

    error_message = None

    if request.method == 'POST':
        action = request.POST.get('_action', '')

        if action == 'reiniciar_ciclo':
            campo.reiniciar_ciclo()
            return redirect('diario_campo_form', campo_id=campo.id)

        tipo_atividade = request.POST.get('tipo_atividade', '').strip()

        # Após a colheita o ciclo é encerrado, mas custos de PÓS-COLHEITA
        # (beneficiamento) ainda podem ser lançados.
        if colheita_done and tipo_atividade != 'pos_colheita':
            error_message = 'A colheita já foi registrada. Só é possível lançar custos de pós-colheita, ou reinicie o ciclo.'
        else:
            data           = request.POST.get('data', '').strip()
            titulo         = request.POST.get('titulo', '').strip()
            detalhe        = request.POST.get('detalhe', '').strip()
            quantidade_unidade = request.POST.get('quantidade_unidade', '').strip()

            if not tipo_atividade:
                error_message = 'Selecione um tipo de atividade.'
            elif not data or not titulo:
                error_message = 'Preencha a data e o título.'
            else:
                # Quantidade
                qtd_raw = request.POST.get('quantidade', '1').strip()
                if tipo_atividade == 'plantio' and 'x' in qtd_raw.lower():
                    try:
                        linhas, colunas = map(int, qtd_raw.lower().split('x'))
                        quantidade = str(linhas * colunas)
                        detalhe = f"{detalhe} | Linhas: {linhas}, Colunas: {colunas}".strip(' |')
                    except ValueError:
                        quantidade = '1'
                else:
                    quantidade = _clean_dec(qtd_raw, '1')

                if tipo_atividade in TIPOS_RECEITA:
                    quantidade_produzida = _clean_dec(request.POST.get('quantidade_produzida', '0'))
                    preco_unitario       = _clean_dec(request.POST.get('preco_unitario', '0'))
                    valor_gasto          = '0'
                    quantidade           = quantidade_produzida
                else:
                    valor_informado      = _clean_dec(request.POST.get('valor_gasto', '0'))
                    modo_gasto           = request.POST.get('_modo_gasto', 'por_unidade')
                    quantidade_produzida = '0'
                    if tipo_atividade in TIPOS_COM_QUANTIDADE and modo_gasto != 'total':
                        # valor informado é POR UNIDADE → total = quantidade × valor
                        try:
                            total = Decimal(quantidade) * Decimal(valor_informado)
                        except (InvalidOperation, TypeError):
                            total = Decimal(valor_informado or '0')
                        valor_gasto    = str(total)
                        preco_unitario = valor_informado   # guarda o valor unitário
                    else:
                        # valor informado já é o TOTAL (modo "total", preparo, plantio…)
                        valor_gasto    = valor_informado
                        preco_unitario = '0'

                Registro.objects.create(
                    campo=campo,
                    data=data,
                    titulo=titulo,
                    detalhe=detalhe,
                    tipo_atividade=tipo_atividade,
                    quantidade=quantidade,
                    quantidade_unidade=quantidade_unidade,
                    valor_gasto=valor_gasto,
                    quantidade_produzida=quantidade_produzida,
                    preco_unitario=preco_unitario,
                    custo_aluguel=campo.custo_aluguel_padrao,
                    custo_manutencao=campo.custo_manutencao_padrao,
                    numero_ciclo=campo.numero_ciclo,
                    ciclos_por_ano=1,
                )

                # Se registrou colheita, fecha o ciclo
                if tipo_atividade == 'colheita':
                    campo.ciclo_ativo = False
                    campo.save(update_fields=['ciclo_ativo'])

                return redirect('diario_campo_form', campo_id=campo.id)

    # Registros do ciclo atual
    registros = campo.registros_ciclo_atual.order_by('-data', '-criado_em')

    # Filtro por tipo (GET)
    filtro_tipo = request.GET.get('tipo', '')
    if filtro_tipo:
        registros = registros.filter(tipo_atividade=filtro_tipo)

    # Busca por título/detalhe
    busca = request.GET.get('q', '').strip()
    if busca:
        from django.db.models import Q
        registros = registros.filter(Q(titulo__icontains=busca) | Q(detalhe__icontains=busca))

    # Totais (sempre do ciclo completo, não filtrado)
    todos_registros = campo.registros_ciclo_atual
    total_gastos  = sum(r.valor_gasto   for r in todos_registros if r.tipo_atividade not in TIPOS_RECEITA)
    total_receita = sum(r.receita_total for r in todos_registros if r.tipo_atividade in TIPOS_RECEITA)
    saldo_ciclo   = total_receita - total_gastos

    # Progresso do ciclo (etapas concluídas)
    etapas = ['preparo_solo', 'plantio', 'adubacao', 'colheita']
    etapas_concluidas = list(
        campo.registros.filter(tipo_atividade__in=etapas, arquivado=False)
                       .values_list('tipo_atividade', flat=True).distinct()
    )

    used_one_time_atividades = list(
        campo.registros.filter(tipo_atividade__in=TIPOS_ONE_TIME, arquivado=False)
                       .values_list('tipo_atividade', flat=True)
    )

    return render(request, 'diario_campo.html', {
        'campo':                    campo,
        'registros':                registros,
        'colheita_done':            colheita_done,
        'error_message':            error_message,
        'atividade_info':           ATIVIDADE_INFO,
        'used_one_time_atividades': used_one_time_atividades,
        'campo_criado_em':          campo.criado_em,
        'total_gastos':             total_gastos,
        'total_receita':            total_receita,
        'saldo_ciclo':              saldo_ciclo,
        'filtro_tipo':              filtro_tipo,
        'busca':                    busca,
        'etapas_concluidas':        etapas_concluidas,
        'num_registros_total':      todos_registros.count(),
    })


@require_http_methods(['GET', 'POST'])
@login_required(login_url="login")
def editar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    error_message = None
    success_message = None

    if request.method == 'POST':
        novo_nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        saca_em_kg = request.POST.get('saca_em_kg', '').strip()
        custo_aluguel_padrao = request.POST.get('custo_aluguel_padrao', '').strip()
        custo_manutencao_padrao = request.POST.get('custo_manutencao_padrao', '').strip()

        def clean_num(v, default='0'):
            try:
                return float(v.replace(',', '.'))
            except Exception:
                return float(default)

        if novo_nome and novo_nome != campo.nome:
            if Campo.objects.filter(usuario=request.user, nome=novo_nome).exclude(id=campo.id).exists():
                error_message = f'Já existe um campo com o nome "{novo_nome}".'
            else:
                campo.nome = novo_nome

        if not error_message:
            campo.descricao             = descricao
            campo.saca_em_kg            = clean_num(saca_em_kg, str(campo.saca_em_kg))
            campo.custo_aluguel_padrao  = clean_num(custo_aluguel_padrao, str(campo.custo_aluguel_padrao))
            campo.custo_manutencao_padrao = clean_num(custo_manutencao_padrao, str(campo.custo_manutencao_padrao))
            campo.save()
            success_message = 'Configurações salvas com sucesso!'

    return render(request, 'editar_campo.html', {
        'campo': campo,
        'error_message': error_message,
        'success_message': success_message,
    })


def download_campo_registros(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    registros = list(campo.registros_ciclo_atual.order_by('-data', '-criado_em'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="diario_{campo.nome}_ciclo{campo.numero_ciclo}.pdf"'
    _render_pdf(response, campo, registros)
    return response


@login_required(login_url="login")
def download_ciclo(request, campo_id, numero_ciclo):
    """Baixa o PDF completo de um ciclo específico do campo (inclui ciclos arquivados)."""
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    registros = list(
        campo.registros.filter(numero_ciclo=numero_ciclo).order_by('-data', '-criado_em')
    )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="diario_{campo.nome}_ciclo{numero_ciclo}.pdf"'
    )
    _render_pdf(response, campo, registros, numero_ciclo=numero_ciclo)
    return response


def _render_pdf_todos(response, campo):
    """Gera um PDF com o histórico COMPLETO do campo (todos os ciclos)."""
    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=14, spaceAfter=6)
    sub_style   = ParagraphStyle('sub',   parent=styles['Normal'], fontSize=9,
                                 textColor=colors.grey, spaceAfter=12)
    ciclo_style = ParagraphStyle('ciclo', parent=styles['Heading2'], fontSize=12,
                                 spaceBefore=16, spaceAfter=6,
                                 textColor=colors.HexColor('#2d6a4f'))

    todos = list(campo.registros.order_by('numero_ciclo', '-data', '-criado_em'))
    ciclos = sorted(set(r.numero_ciclo for r in todos))

    g_gastos  = sum(r.valor_gasto   for r in todos if r.tipo_atividade not in TIPOS_RECEITA)
    g_receita = sum(r.receita_total for r in todos if r.tipo_atividade in TIPOS_RECEITA)

    elements = [
        Paragraph(f"Diário de Campo — {campo.nome}", title_style),
        Paragraph(f"Histórico completo  ·  {len(ciclos)} ciclo(s)  ·  {len(todos)} registro(s)  ·  "
                  f"Gastos: R$ {g_gastos:.2f}  ·  Receita: R$ {g_receita:.2f}  ·  "
                  f"Saldo: R$ {g_receita - g_gastos:.2f}", sub_style),
    ]

    table_style = TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#2d6a4f')),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7f3')]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])

    if not todos:
        elements.append(Paragraph("Nenhum registro neste campo.", styles['Normal']))
    else:
        for nc in ciclos:
            regs = [r for r in todos if r.numero_ciclo == nc]
            cg = sum(r.valor_gasto   for r in regs if r.tipo_atividade not in TIPOS_RECEITA)
            cr = sum(r.receita_total for r in regs if r.tipo_atividade in TIPOS_RECEITA)
            atual = ' (atual)' if nc == campo.numero_ciclo else ''
            elements.append(Paragraph(
                f"Ciclo {nc}{atual}  —  {len(regs)} registro(s)  ·  "
                f"Gastos R$ {cg:.2f}  ·  Receita R$ {cr:.2f}  ·  Saldo R$ {cr - cg:.2f}",
                ciclo_style))
            table = Table(_build_pdf_table(regs), repeatRows=1)
            table.setStyle(table_style)
            elements.append(table)

    doc.build(elements)


@login_required(login_url="login")
def download_todos_ciclos(request, campo_id):
    """Baixa o PDF com TODOS os ciclos do campo (arquivados + atual)."""
    campo = get_object_or_404(Campo, id=campo_id, usuario=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="diario_{campo.nome}_TODOS_os_ciclos.pdf"'
    )
    _render_pdf_todos(response, campo)
    return response


def download_registro(request, registro_id):
    registro = get_object_or_404(Registro, id=registro_id)
    campo = registro.campo

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="registro_{registro.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=13, spaceAfter=12)

    rows = [
        ['Campo',        campo.nome],
        ['Data',         registro.data.strftime('%d/%m/%Y')],
        ['Atividade',    registro.get_tipo_atividade_display() if registro.tipo_atividade else '—'],
        ['Título',       registro.titulo],
        ['Observações',  registro.detalhe or '—'],
        ['Quantidade',   f"{registro.quantidade} {registro.quantidade_unidade}".strip()],
        ['Valor Gasto',  f"R$ {registro.valor_gasto:.2f}"],
    ]
    if registro.tipo_atividade == 'colheita':
        rows += [
            ['Qtd Produzida', f"{registro.quantidade_produzida} {registro.quantidade_unidade}".strip()],
            ['Preço Unit.',   f"R$ {registro.preco_unitario:.2f}"],
            ['Receita Total', f"R$ {registro.receita_total:.2f}"],
        ]

    table = Table(rows, colWidths=[5*cm, None])
    table.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (0, -1),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS',(0, 0), (-1, -1), [colors.white, colors.HexColor('#f0f7f3')]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    doc.build([
        Paragraph(f"Registro — {registro.titulo}", title_style),
        table,
    ])
    return response


# Mantido por compatibilidade com URL antiga
download_registros = download_campo_registros