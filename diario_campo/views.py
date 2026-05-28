from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from .models import Campo, Registro
from django.views.decorators.http import require_http_methods

# Create your views here.

def selecionar_campo(request):
    if request.method == 'POST':
        nome = request.POST.get('nome_campo', '').strip()
        if nome:
            campo, created = Campo.objects.get_or_create(nome=nome)
            return redirect('diario_campo_form', campo_id=campo.id)

    campos = Campo.objects.all().order_by('nome')
    return render(request, 'selecionar_campo.html', {'campos': campos})


def excluir_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    if request.method == 'POST':
        campo.delete()
    return redirect('diario_campo')


def excluir_registro(request, registro_id):
    registro = get_object_or_404(Registro, id=registro_id)
    campo_id = registro.campo.id
    if request.method == 'POST':
        registro.delete()
    return redirect('diario_campo_form', campo_id=campo_id)


def diario_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    colheita_done = campo.registros.filter(tipo_atividade='colheita').exists()

    error_message = None
    if request.method == 'POST':
        if colheita_done:
            error_message = 'A colheita já foi registrada para este campo. Novos registros não são permitidos.'
        else:
            data = request.POST.get('data')
            titulo = request.POST.get('titulo', '').strip()
            detalhe = request.POST.get('detalhe', '').strip()
            tipo_atividade = request.POST.get('tipo_atividade', '').strip()
            quantidade_unidade = request.POST.get('quantidade_unidade', '').strip()
            recurso_tipo = request.POST.get('recurso_tipo', '').strip()
            medida_tipo = request.POST.get('medida_tipo', '').strip()

            def clean_number(value):
                return value.replace(',', '.').strip() if value else '0'

            quantidade_raw = request.POST.get('quantidade', '0').strip()
            if tipo_atividade == 'plantio' and 'x' in quantidade_raw:
                # Parse linhas x colunas
                try:
                    linhas, colunas = map(int, quantidade_raw.split('x'))
                    quantidade = str(linhas * colunas)
                    detalhe += f" (Linhas: {linhas}, Colunas: {colunas})"
                except ValueError:
                    quantidade = '0'
            else:
                quantidade = clean_number(quantidade_raw)
            valor_gasto = clean_number(request.POST.get('valor_gasto', '0'))
            quantidade_produzida = clean_number(request.POST.get('quantidade_produzida', '0'))
            preco_unitario = clean_number(request.POST.get('preco_unitario', '0'))
            custo_sementes = clean_number(request.POST.get('custo_sementes', '0'))
            custo_adubo = clean_number(request.POST.get('custo_adubo', '0'))
            custo_defensivos = clean_number(request.POST.get('custo_defensivos', '0'))
            custo_agua = clean_number(request.POST.get('custo_agua', '0'))
            custo_mao_obra = clean_number(request.POST.get('custo_mao_obra', '0'))
            custo_energia = clean_number(request.POST.get('custo_energia', '0'))
            custo_colheita = clean_number(request.POST.get('custo_colheita', '0'))
            custo_transporte = clean_number(request.POST.get('custo_transporte', '0'))
            custo_aluguel = request.POST.get('custo_aluguel', '').strip()
            custo_manutencao = request.POST.get('custo_manutencao', '').strip()
            ciclos_por_ano = clean_number(request.POST.get('ciclos_por_ano', '1'))
            try:
                ciclos_por_ano = int(float(ciclos_por_ano))
                if ciclos_por_ano < 1:
                    ciclos_por_ano = 1
            except Exception:
                ciclos_por_ano = 1

            # If this is a colheita, attempt to derive preco_unitario from valor_gasto / quantidade_produzida
            try:
                qtd_prod_val = float(quantidade_produzida.replace(',', '.')) if quantidade_produzida else 0.0
            except Exception:
                qtd_prod_val = 0.0

            try:
                valor_gasto_val = float(valor_gasto.replace(',', '.')) if valor_gasto else 0.0
            except Exception:
                valor_gasto_val = 0.0

            try:
                preco_unit_val = float(preco_unitario.replace(',', '.')) if preco_unitario else 0.0
            except Exception:
                preco_unit_val = 0.0

            if tipo_atividade == 'colheita' and (not preco_unit_val or preco_unit_val == 0) and qtd_prod_val and valor_gasto_val:
                try:
                    preco_unit_val = valor_gasto_val / qtd_prod_val
                    preco_unitario = str(round(preco_unit_val, 2))
                except Exception:
                    preco_unitario = preco_unitario

            if not tipo_atividade:
                error_message = 'Selecione um tipo de atividade antes de salvar.'
            elif data and titulo:
                detalhe_final = detalhe
                detalhe_ciclos = []
                if recurso_tipo:
                    detalhe_ciclos.append(f"Recurso: {recurso_tipo}")
                if medida_tipo:
                    detalhe_ciclos.append(f"Medida: {medida_tipo}")
                if detalhe_ciclos:
                    detalhe_final = f"{detalhe_final} | {' | '.join(detalhe_ciclos)}" if detalhe_final else ' | '.join(detalhe_ciclos)

                # decide valores de aluguel/manutenção: usa valores informados ou default do campo
                try:
                    aluguel_to_save = float(custo_aluguel.replace(',', '.')) if custo_aluguel not in (None, '', '0') else float(campo.custo_aluguel_padrao)
                except Exception:
                    aluguel_to_save = float(campo.custo_aluguel_padrao)

                try:
                    manut_to_save = float(custo_manutencao.replace(',', '.')) if custo_manutencao not in (None, '', '0') else float(campo.custo_manutencao_padrao)
                except Exception:
                    manut_to_save = float(campo.custo_manutencao_padrao)

                # Convert quantidade_produzida from 'saca' to kg if needed for internal consistency? We store raw value and unit;
                # finance view will convert when aggregating.

                Registro.objects.create(
                    campo=campo,
                    data=data,
                    titulo=titulo,
                    detalhe=detalhe_final,
                    tipo_atividade=tipo_atividade,
                    quantidade=quantidade,
                    quantidade_unidade=quantidade_unidade,
                    recurso_tipo=recurso_tipo,
                    medida_tipo=medida_tipo,
                    valor_gasto=valor_gasto,
                    quantidade_produzida=quantidade_produzida,
                    preco_unitario=preco_unitario,
                    custo_sementes=custo_sementes,
                    custo_adubo=custo_adubo,
                    custo_defensivos=custo_defensivos,
                    custo_agua=custo_agua,
                    custo_mao_obra=custo_mao_obra,
                    custo_energia=custo_energia,
                    custo_colheita=custo_colheita,
                    custo_transporte=custo_transporte,
                    custo_aluguel=aluguel_to_save,
                    custo_manutencao=manut_to_save,
                    ciclos_por_ano=ciclos_por_ano,
                )
                return redirect('diario_campo_form', campo_id=campo.id)
            else:
                error_message = 'Preencha a data e o título antes de salvar.'

    registros = campo.registros.all()

    atividade_info = [
        {'value': 'preparo_solo', 'label': 'Preparo do Solo', 'one_time': True},
        {'value': 'plantio', 'label': 'Plantio', 'one_time': True},
        {'value': 'adubacao', 'label': 'Adubação', 'one_time': False},
        {'value': 'irrigacao', 'label': 'Irrigação', 'one_time': False},
        {'value': 'capina', 'label': 'Capina / Controle de Mato', 'one_time': False},
        {'value': 'controle_pragas_doencas', 'label': 'Controle de Pragas e Doenças', 'one_time': False},
        {'value': 'energia_combustivel', 'label': 'Energia / Combustível', 'one_time': False},
        {'value': 'transporte_embalagem', 'label': 'Transporte / Embalagem', 'one_time': False},
        {'value': 'colheita', 'label': 'Colheita', 'one_time': True},
    ]

    used_one_time_atividades = []
    if campo.registros.filter(tipo_atividade__in=['preparo_solo', 'plantio', 'colheita']).exists():
        used_one_time_atividades = list(campo.registros.filter(tipo_atividade__in=['preparo_solo', 'plantio', 'colheita']).values_list('tipo_atividade', flat=True))

    return render(request, 'diario_campo.html', {
        'campo': campo,
        'registros': registros,
        'colheita_done': colheita_done,
        'error_message': error_message,
        'atividade_info': atividade_info,
        'used_one_time_atividades': used_one_time_atividades,
        'form_data': request.POST,
    })


def download_registros(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    registros = campo.registros.all().order_by('-data', '-criado_em')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historico_registros_{campo.nome}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"Histórico de Registros - Campo: {campo.nome}", styles['Title'])
    elements.append(title)

    data = [
        ['Data', 'Tipo', 'Título', 'Quantidade', 'Unidade', 'Recurso', 'Medida', 'Valor Gasto', 'Qtd Produzida', 'Preço Unit.', 'Custo Total (R$)'],
    ]
    for registro in registros:
        data.append([
            registro.data.strftime('%d/%m/%Y'),
            registro.get_tipo_atividade_display() if registro.tipo_atividade else 'N/A',
            registro.titulo,
            str(registro.quantidade),
            registro.quantidade_unidade or 'N/A',
            registro.recurso_tipo or 'N/A',
            registro.medida_tipo or 'N/A',
            f"R$ {registro.valor_gasto:.2f}",
            str(registro.quantidade_produzida),
            f"R$ {registro.preco_unitario:.2f}",
            f"R$ {registro.custo_total_ciclo:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    return response


def download_registro(request, registro_id):
    registro = get_object_or_404(Registro, id=registro_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="registro_{registro.titulo}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"Registro: {registro.titulo}", styles['Title'])
    elements.append(title)

    data = [
        ['Campo', registro.campo.nome],
        ['Data', registro.data.strftime('%d/%m/%Y')],
        ['Atividade', registro.get_tipo_atividade_display() if registro.tipo_atividade else 'N/A'],
        ['Título', registro.titulo],
        ['Detalhe', registro.detalhe],
        ['Recurso', registro.recurso_tipo or 'N/A'],
        ['Medida', registro.medida_tipo or 'N/A'],
        ['Quantidade', f"{registro.quantidade} {registro.quantidade_unidade}".strip()],
        ['Valor Gasto', f"R$ {registro.valor_gasto:.2f}"],
        ['Quantidade Produzida', str(registro.quantidade_produzida)],
        ['Preço Unitário', f"R$ {registro.preco_unitario:.2f}"],
        ['Custo Total (por ciclo)', f"R$ {registro.custo_total_ciclo:.2f}"],
        ['Receita Total', f"R$ {registro.receita_total:.2f}"],
        ['Lucro Total', f"R$ {registro.lucro_total:.2f}"],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    return response


@require_http_methods(['GET', 'POST'])
def editar_campo(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    error_message = None
    if request.method == 'POST':
        saca_em_kg = request.POST.get('saca_em_kg', '').strip()
        custo_aluguel_padrao = request.POST.get('custo_aluguel_padrao', '').strip()
        custo_manutencao_padrao = request.POST.get('custo_manutencao_padrao', '').strip()

        def clean_num(v, default='0'):
            try:
                return float(v.replace(',', '.'))
            except Exception:
                return float(default)

        campo.saca_em_kg = clean_num(saca_em_kg, str(campo.saca_em_kg))
        campo.custo_aluguel_padrao = clean_num(custo_aluguel_padrao, str(campo.custo_aluguel_padrao))
        campo.custo_manutencao_padrao = clean_num(custo_manutencao_padrao, str(campo.custo_manutencao_padrao))
        campo.save()
        return redirect('diario_campo_form', campo_id=campo.id)

    return render(request, 'editar_campo.html', {
        'campo': campo,
        'error_message': error_message,
    })


def download_campo_registros(request, campo_id):
    campo = get_object_or_404(Campo, id=campo_id)
    registros = campo.registros.all().order_by('-data', '-criado_em')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="registros_{campo.nome}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"Histórico de Registros - Campo: {campo.nome}", styles['Title'])
    elements.append(title)

    data = [
        ['Data', 'Tipo', 'Título', 'Quantidade', 'Unidade', 'Recurso', 'Medida', 'Valor Gasto', 'Qtd Produzida', 'Preço Unit.', 'Custo Total (R$)'],
    ]
    for registro in registros:
        data.append([
            registro.data.strftime('%d/%m/%Y'),
            registro.get_tipo_atividade_display() if registro.tipo_atividade else 'N/A',
            registro.titulo,
            str(registro.quantidade),
            registro.quantidade_unidade or 'N/A',
            registro.recurso_tipo or 'N/A',
            registro.medida_tipo or 'N/A',
            f"R$ {registro.valor_gasto:.2f}",
            str(registro.quantidade_produzida),
            f"R$ {registro.preco_unitario:.2f}",
            f"R$ {registro.custo_total_ciclo:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    return response