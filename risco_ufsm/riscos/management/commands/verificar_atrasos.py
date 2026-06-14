'''Comando para marcar tratamentos vencidos como atrasados.'''

from django.core.management.base import BaseCommand
from django.utils import timezone
from riscos.models import TratamentoRisco, Notificacao


class Command(BaseCommand):
    help = 'Marca tratamentos vencidos como Atrasado e gera notificações.'

    def handle(self, *args, **options):
        hoje = timezone.localdate()
        atrasados = TratamentoRisco.objects.filter(
            data_conclusao_prevista__lt=hoje,
            situacao__in=['NAO_INICIADO', 'EM_EXECUCAO']
        ).select_related('plano__setor', 'plano__criado_por')

        for t in atrasados:
            t.situacao = 'ATRASADO'
            t.save(update_fields=['situacao'])

            # Criar notificação para o criador do plano se ainda não existir
            Notificacao.objects.get_or_create(
                usuario=t.plano.criado_por,
                plano=t.plano,
                tipo=Notificacao.TIPO_ATRASO,
                lida=False,
                defaults={'mensagem': f'O plano #{t.plano.pk} do setor {t.plano.setor} '
                                      f'está com tratamento atrasado.'}
            )
        self.stdout.write(f'{atrasados.count()} planos marcados como atrasados.')
