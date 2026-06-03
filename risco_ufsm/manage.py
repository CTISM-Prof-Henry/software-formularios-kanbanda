"""Utilitário de linha de comando do Django."""

import os
import sys

def main():
    """Executa tarefas administrativas do Django."""

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risco_ufsm.settings')
    try:
        from django.core.management import execute_from_command_line # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError('Django não instalado ou virtualenv não ativado.') from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
