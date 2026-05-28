from diario_campo.models import Campo, Registro

for c in Campo.objects.all():
    col = Registro.objects.filter(campo=c, tipo_atividade='colheita')
    print('Campo:', c.nome, 'colheitas:', col.count())
    for r in col:
        print('-', r.id, r.data, r.quantidade_produzida, r.preco_unitario, r.valor_gasto)
    print('---')
