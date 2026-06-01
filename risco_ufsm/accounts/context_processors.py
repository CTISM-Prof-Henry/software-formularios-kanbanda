from .models import Perfil


def menu_lateral(request):
    """
    Injeta o menu lateral dinâmico baseado no perfil do usuário.
    Usado em todos os templates do sistema.
    só mostra o que o usuário tem permissão para acessar, baseado nas propriedades do perfil.
    """
    if not request.user.is_authenticated:
        return {}

    u = request.user

    menu = [
        {
            'label': 'Painel',
            'icone': 'home',
            'url_name': 'painel',
            'visivel': True,
        },
        {
            'label': 'Usuários',
            'icone': 'users',
            'url_name': 'lista_usuarios',
            'visivel': u.pode_gerenciar_usuarios,
            'subitens': [
                {
                    'label': 'Listar Usuários',
                    'url_name': 'lista_usuarios',
                    'visivel': u.pode_gerenciar_usuarios,
                },
                {
                    'label': 'Novo Usuário',
                    'url_name': 'cadastro_usuario',
                    'visivel': u.pode_criar_usuario,
                },
            ],
        },
        {
            'label': 'Meu Perfil',
            'icone': 'user',
            'url_name': 'meu_perfil',
            'visivel': True,
        },
        {
            'label': 'Logs de Acesso',
            'icone': 'shield',
            'url_name': 'logs_acesso',
            'visivel': u.pode_ver_logs,
        },
    ]

    # Filtra itens invisíveis
    menu_filtrado = [item for item in menu if item.get('visivel')]
    for item in menu_filtrado:
        if 'subitens' in item:
            item['subitens'] = [s for s in item['subitens'] if s.get('visivel')]

    return {'menu_lateral': menu_filtrado}
