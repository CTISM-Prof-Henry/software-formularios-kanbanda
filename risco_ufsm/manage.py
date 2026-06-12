'''Arquivo de gerenciamento do Django para o projeto.'''
# pylint: disable=import-outside-toplevel
# desabilitei a importação fora do nível superior para evitar erros

import os
import sys

def main():
    '''Ponto de entrada para o gerenciamento do Django.'''
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risco_ufsm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError('Django não instalado ou virtualenv não ativado.') from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
