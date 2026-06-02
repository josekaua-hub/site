from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diario_campo', '0002_campo_ciclo_registro_ciclo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Remover o unique constraint antigo do nome
        migrations.AlterField(
            model_name='campo',
            name='nome',
            field=models.CharField(max_length=100),
        ),
        # 2. Adicionar FK com default=1 (primeiro superuser) para campos existentes
        migrations.AddField(
            model_name='campo',
            name='usuario',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='campos',
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        # 3. Aplicar unique_together
        migrations.AlterUniqueTogether(
            name='campo',
            unique_together={('usuario', 'nome')},
        ),
    ]
