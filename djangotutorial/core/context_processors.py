from django.conf import settings


def notificacao_ms(request):
    """
    Disponibiliza as configuracoes do microservico de notificacao
    em todos os templates.
    """
    context = {
        'NOTIFICACAO_MS_URL': settings.NOTIFICACAO_MS_URL,
        'NOTIFICACAO_MS_API_KEY': settings.NOTIFICACAO_MS_API_KEY,
    }

    # Passa o user_id se o usuario estiver logado
    if request.user.is_authenticated:
        context['NOTIFICACAO_USER_ID'] = request.user.id

    return context