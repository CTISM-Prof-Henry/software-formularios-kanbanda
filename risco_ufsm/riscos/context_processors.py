'''Context processors do app riscos.'''


def notificacoes(request):
    '''Disponibiliza a contagem de notificações não lidas no header.'''
    if not request.user.is_authenticated:
        return {}
    from riscos.models import Notificacao
    count = Notificacao.objects.filter(usuario=request.user, lida=False).count()
    return {'notificacoes_count': count}
