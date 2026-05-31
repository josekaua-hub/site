from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Campo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('descricao', models.TextField(blank=True)),
                ('saca_em_kg', models.DecimalField(decimal_places=2, default=50.0, help_text='Quantos kg tem uma saca (padrão)', max_digits=7)),
                ('custo_aluguel_padrao', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('custo_manutencao_padrao', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registros', to='diario_campo.campo')),
                ('data', models.DateField()),
                ('titulo', models.CharField(max_length=200)),
                ('detalhe', models.TextField(blank=True)),
                ('tipo_atividade', models.CharField(
                    blank=True, default='', max_length=30,
                    choices=[
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
                )),
                ('quantidade', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('quantidade_unidade', models.CharField(blank=True, default='', max_length=50)),
                ('recurso_tipo', models.CharField(blank=True, default='', max_length=50)),
                ('medida_tipo', models.CharField(blank=True, default='', max_length=50)),
                ('valor_gasto', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('quantidade_produzida', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('preco_unitario', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_sementes', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_adubo', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_defensivos', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_agua', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_mao_obra', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_energia', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_colheita', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_transporte', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_aluguel', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('custo_manutencao', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('ciclos_por_ano', models.PositiveSmallIntegerField(default=1)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-data', '-criado_em'],
            },
        ),
    ]
