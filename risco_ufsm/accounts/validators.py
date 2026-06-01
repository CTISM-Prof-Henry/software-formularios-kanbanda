import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SenhaForteValidator:
    """
    Exige ao menos: 1 maiúscula, 1 minúscula, 1 dígito, 1 caractere especial.
    """

    def validate(self, password, user=None):
        erros = []
        if not re.search(r'[A-Z]', password):
            erros.append('pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', password):
            erros.append('pelo menos uma letra minúscula')
        if not re.search(r'\d', password):
            erros.append('pelo menos um número')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            erros.append('pelo menos um caractere especial (!@#$%...)')
        if erros:
            raise ValidationError(
                f'A senha deve conter: {", ".join(erros)}.',
                code='senha_fraca',
            )

    def get_help_text(self):
        return _(
            'A senha deve ter no mínimo 8 caracteres com letras maiúsculas, '
            'minúsculas, números e caracteres especiais.'
        )
