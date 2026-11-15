# Generated for Sprint 3 & 4 fields (H15, H17, H18, H19)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='estoque_baixado',
            field=models.BooleanField(default=False, verbose_name='Estoque Baixado'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='aprovada_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Aprovada em'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='data_conclusao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Concluída em'),
        ),
        migrations.AddField(
            model_name='itempeca',
            name='quantidade_utilizada',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantidade Utilizada'),
        ),
    ]

