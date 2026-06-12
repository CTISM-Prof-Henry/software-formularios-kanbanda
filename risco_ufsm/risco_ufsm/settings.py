"""Configurações do projeto Django risco_ufsm."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Segredo e modo ────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-ufsm-dev-only-troque-em-producao-2024'
)
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
_allowed = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = _allowed.split(',') if _allowed \
    else (['*'] if DEBUG else ['localhost', '127.0.0.1'])

# ── Aplicações ────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceiros
    'simple_history',
    # Próprias
    'accounts.apps.AccountsConfig',
    'organizacional.apps.OrganizacionalConfig',
    'auditoria.apps.AuditoriaConfig',
    'configuracao.apps.ConfiguracaoConfig',
    'riscos.apps.RiscosConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    # Middleware customizado de segurança
    'accounts.middleware.SessaoExpiradaMiddleware',
    'accounts.middleware.BruteForceMiddleware',
]

ROOT_URLCONF = 'risco_ufsm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.menu_lateral',
            ],
        },
    },
]

WSGI_APPLICATION = 'risco_ufsm.wsgi.application'

# ── Banco de dados ────────────────────────────────────────────────────────────
_use_sqlite = os.environ.get('USE_SQLITE', 'true').lower() == 'true'

if _use_sqlite:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME':     os.environ.get('DB_NAME',     'risco_ufsm'),
            'USER':     os.environ.get('DB_USER',     'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', '1234'),
            'HOST':     os.environ.get('DB_HOST',     'localhost'),
            'PORT':     os.environ.get('DB_PORT',     '5432'),
            'OPTIONS':  {'connect_timeout': 10},
        }
    }

# ── Autenticação ──────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.Usuario'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.MatriculaEmailBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'accounts.validators.SenhaForteValidator'},
]

LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/painel/'
LOGOUT_REDIRECT_URL = '/login/'

# ── Sessão e segurança ────────────────────────────────────────────────────────
SESSION_COOKIE_AGE           = int(os.environ.get('SESSION_COOKIE_AGE', 1800))  # 30 min
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST   = True        # renova a sessão a cada request
CSRF_COOKIE_HTTPONLY         = True
SESSION_COOKIE_SECURE        = not DEBUG   # HTTPS em produção
CSRF_COOKIE_SECURE           = not DEBUG
SECURE_BROWSER_XSS_FILTER    = True
X_FRAME_OPTIONS              = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF  = True

# Proteção brute force (via cache/DB)
BRUTE_FORCE_MAX_TENTATIVAS   = int(os.environ.get('BRUTE_FORCE_MAX_TENTATIVAS', 5))
BRUTE_FORCE_BLOQUEIO_MINUTOS = int(os.environ.get('BRUTE_FORCE_BLOQUEIO_MINUTOS', 15))

# Tokens
TOKEN_ATIVACAO_HORAS         = int(os.environ.get('TOKEN_ATIVACAO_HORAS', 48))
TOKEN_RECUPERACAO_MINUTOS    = int(os.environ.get('TOKEN_RECUPERACAO_MINUTOS', 15))

# URL base para links nos e-mails
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# ── Cache (usado para rate limiting) ─────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'gr-ufsm-cache',
    }
}

# ── E-mail ────────────────────────────────────────────────────────────────────
_email_backend = os.environ.get('EMAIL_BACKEND', 'console')

if _email_backend == 'console':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND   = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST      = os.environ.get('EMAIL_HOST', 'smtp.ufsm.br')
    EMAIL_PORT      = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS   = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'GR-UFSM <noreply@ufsm.br>')

# ── Internacionalização ───────────────────────────────────────────────────────
LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'America/Sao_Paulo'
USE_I18N      = True
USE_TZ        = True

# ── Arquivos estáticos e de mídia ─────────────────────────────────────────────
STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'accounts': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'auditoria': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
