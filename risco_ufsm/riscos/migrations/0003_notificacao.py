# Generated for Parte 4 - Relatorio PDF e notificacoes

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('riscos', '0002_alter_identificacaorisco_consequencias'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('ATRASO',
                                                    'Plano de Tratamento Atrasado')],
                                          max_length=20)),
                ('mensagem', models.TextField()),
                ('lida', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('plano', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='notificacoes',
                                            to='riscos.planoderisco')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='notificacoes',
                                              to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificação',
                'ordering': ['-criado_em'],
            },
        ),
    ]
