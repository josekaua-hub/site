from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adiciona suporte a múltiplos ciclos:
    - Campo: ciclo_ativo (bool) e numero_ciclo (int)
    - Registro: numero_ciclo (int) e arquivado (bool)
    """

    dependencies = [
        ('diario_campo', '0001_initial'),
    ]

    operations = [
        # Novos campos em Campo
        migrations.AddField(
            model_name='campo',
            name='ciclo_ativo',
            field=models.BooleanField(
                default=True,
                help_text='Se False, o ciclo está encerrado (colheita feita)',
            ),
        ),
        migrations.AddField(
            model_name='campo',
            name='numero_ciclo',
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text='Número sequencial do ciclo atual',
            ),
        ),
        # Novos campos em Registro
        migrations.AddField(
            model_name='registro',
            name='numero_ciclo',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='registro',
            name='arquivado',
            field=models.BooleanField(
                default=False,
                help_text='True quando o ciclo foi encerrado e reiniciado',
            ),
        ),
        # Marca campos que já têm colheita como ciclo encerrado
        migrations.RunSQL(
            sql="""
                UPDATE diario_campo_campo
                SET ciclo_ativo = false
                WHERE id IN (
                    SELECT DISTINCT campo_id
                    FROM diario_campo_registro
                    WHERE tipo_atividade = 'colheita'
                );
            """,
            reverse_sql="UPDATE diario_campo_campo SET ciclo_ativo = true;",
        ),
    ]