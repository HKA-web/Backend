import os
import sys
import yaml
import logging
import platform
import structlog
from pathlib import Path
from huey import RedisHuey, MemoryHuey
from django.utils.log import RequireDebugTrue

# === BASE PATH SETUP ===========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / 'apps'

for path in (BASE_DIR, APPS_DIR):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# === AUTO SCAN APP =============================================================
AUTO_APPS = []
if APPS_DIR.exists():
    for app in APPS_DIR.iterdir():
        if app.is_dir() and (app / '__init__.py').exists():
            AUTO_APPS.append(app.name)

for app in BASE_DIR.iterdir():
    if app.is_dir() and (app / '__init__.py').exists():
        if app.name not in AUTO_APPS and app.name not in ['config', 'apps', '__pycache__']:
            AUTO_APPS.append(app.name)

# === CLEAR TERMINAL DAN LIST APP ==============================================
if os.environ.get('RUN_MAIN') == 'true':
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print('\n Django Auto App Scanner\n' + '=' * 35)
    for i, app in enumerate(AUTO_APPS, start=1):
        print(f'  {i:02d}. {app}')
    print('=' * 35)
    print(f' Total {len(AUTO_APPS)} app terdeteksi.\n')

# === LOAD CONFIG YAML ==========================================================
CONFIG_PATH = BASE_DIR / 'config.yaml'
CONFIG = {}

if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            CONFIG = yaml.safe_load(f) or {}
            print('[INFO] config.yaml loaded successfully.')
    except Exception as e:
        print(f'[WARN] Gagal membaca config.yaml: {e}')
else:
    print('[WARN] config.yaml tidak ditemukan, menggunakan default setting.')

HUEY_CONF = CONFIG.get('huey', {})
REDIS_CONF = CONFIG.get('redis', {})
WEBHOOK_CONF = CONFIG.get('webhook', {})

# === SERVER CONFIG =============================================================
SERVER_CONF = CONFIG.get('server', {})

DEBUG = SERVER_CONF.get('debug', True)
ALLOWED_HOSTS = SERVER_CONF.get('allowed_hosts', ['*'])
NODE_API_URL = SERVER_CONF.get('node_api', 'http://localhost:3000/api/send-messages')
AI_AGENT_URL = SERVER_CONF.get('ai_api', 'http://localhost:5678/webhook/user-request')
RETRY = SERVER_CONF.get('retry', 1)
AI_AGENT = SERVER_CONF.get('ai_agent', False)
STANDALONE = SERVER_CONF.get('standalone', False)

# === DJANGO CORE SETTINGS ======================================================
SECRET_KEY = CONFIG.get('secret_key', 'django-insecure-xs_%_86*c_@y&wj+d3sswr_l2e-x8p@ewp-sety*f&gv+6hg__')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'huey.contrib.djhuey',
    *AUTO_APPS,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# === DATABASE ==================================================================
DATABASES = {}
for alias, db_conf in CONFIG.get('databases', {}).items():
    # SQL Server tidak pakai Django engine
    if alias == 'sqlserver':
        continue

    db_conf = {k.lower(): v for k, v in db_conf.items()}

    if 'engine' in db_conf:
        DATABASES[alias] = {
            'ENGINE': db_conf.get('engine'),
            'NAME': db_conf.get('name'),
            'USER': db_conf.get('user', ''),
            'PASSWORD': db_conf.get('password', ''),
            'HOST': db_conf.get('host', 'localhost'),
            'PORT': db_conf.get('port', ''),
        }

        if 'options' in db_conf:
            DATABASES[alias]['OPTIONS'] = db_conf['options']

if 'default' not in DATABASES:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '111111',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {'options': '-c search_path=public'},
    }

# SQL Server (non-Django)
SQLSERVER_DEFAULT = CONFIG.get('databases', {}).get('sqlserver', {})

# === REDIS =======================================================
REDIS_HOST = HUEY_CONF.get('host') or REDIS_CONF.get('host', '127.0.0.1')
REDIS_PORT = HUEY_CONF.get('port') or REDIS_CONF.get('port', 6379)
REDIS_DB   = HUEY_CONF.get('db') or REDIS_CONF.get('db', 5)
REDIS_PASS = HUEY_CONF.get('password') or REDIS_CONF.get('password')

# === HUEY CONFIG ===============================================================
HUEY_IMMEDIATE = HUEY_CONF.get("immediate", False)

USE_MEMORY_HUEY = DEBUG and HUEY_IMMEDIATE

if USE_MEMORY_HUEY:
    HUEY = MemoryHuey(
        name=HUEY_CONF.get("name", "dev-huey"),
        immediate=True,
    )

else:
    HUEY = RedisHuey(
        name=HUEY_CONF.get("name", "backend-huey"),
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        db=int(REDIS_DB),
        password=REDIS_PASS,
        results=HUEY_CONF.get("results", True),
        store_errors=HUEY_CONF.get("store_errors", True),
        utc=True,
        blocking=True,
        read_timeout=1,
        immediate=False,
    )

# === WEBHOOK =======================================================
WEBHOOK_USER = HUEY_CONF.get('user') or WEBHOOK_CONF.get('user', 'root')
WEBHOOK_PASS = HUEY_CONF.get('password') or WEBHOOK_CONF.get('password', '#Admin#')
WEBHOOK_URL   = HUEY_CONF.get('url') or WEBHOOK_CONF.get('url', 'http://localhost:8000')
WEBHOOK_ACCESS   = HUEY_CONF.get('access') or WEBHOOK_CONF.get('access', '123')
WEBHOOK_REFRESH   = HUEY_CONF.get('refresh') or WEBHOOK_CONF.get('refresh', '321')

# === VALIDATION & LOCALE =======================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = CONFIG.get('language_code', 'en-us')
TIME_ZONE = CONFIG.get('time_zone', 'UTC')
USE_I18N = True
USE_TZ = True

# === STATIC FILES ==============================================================
STATIC_URL = CONFIG.get('static_url', 'static/')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === STRUCTLOG (Colored Logging) ===============================================
RESET = '\033[0m'
COLORS = {
    'DEBUG': '\033[34m',
    'INFO': '\033[32m',
    'WARNING': '\033[33m',
    'ERROR': '\033[31m',
    'CRITICAL': '\033[35m',
    'SQL': '\033[36m',
}

class ColoredConsoleRenderer(structlog.dev.ConsoleRenderer):
    def __call__(self, logger, name, event_dict):
        level = event_dict.get('level', 'INFO').upper()
        msg = event_dict.get('event', '')
        logger_name = event_dict.get('logger', '')
        color = COLORS.get(level, RESET)

        if 'django.db.backends' in logger_name or 'SELECT' in msg:
            level = 'SQL'
            color = COLORS['SQL']

        formatted = f'{color}[{level:<7}] {logger_name:<30} | {msg}{RESET}'
        return formatted

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt='%H:%M:%S'),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.UnicodeDecoder(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    logger_factory=structlog.stdlib.LoggerFactory(),
)

if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'colored': {
                '()': structlog.stdlib.ProcessorFormatter,
                'processor': ColoredConsoleRenderer(),
                'foreign_pre_chain': [
                    structlog.processors.TimeStamper(fmt='%H:%M:%S'),
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                ],
            },
        },
        'filters': {'require_debug_true': {'()': RequireDebugTrue}},
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
            },
        },
        'loggers': {
            'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
            'django.server': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
            'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        },
    }
