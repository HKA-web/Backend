import os
import yaml
from pathlib import Path

# -----------------------------
# Base directory
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Service name
# -----------------------------
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'users-service')

# -----------------------------
# Load config.yaml
# -----------------------------
with open(BASE_DIR / 'config.yaml') as f:
    CONFIG = yaml.safe_load(f)

# -----------------------------
# Security
# -----------------------------
SECRET_KEY = CONFIG['server'].get(
    'secret_key',
    'django-insecure-$2of$_!*kpie7%j-runx!p=zf#uh($abdx%(-imd&h)v_o@oy4'
)
DEBUG = CONFIG['server'].get('debug', True)
ALLOWED_HOSTS = CONFIG.get('allowed_hosts', ['*'])

# -----------------------------
# Server-specific workers (Huey)
# -----------------------------
SERVER_CONFIG = CONFIG.get("server", {}) 

# -----------------------------
# Application
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'authentication',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# -----------------------------
# Database
# -----------------------------
DATABASES = {}
for alias, db_conf in CONFIG.get('databases', {}).items():
    DATABASES[alias] = {
        'ENGINE': db_conf['engine'],
        'NAME': db_conf['name'],
        'USER': db_conf['user'],
        'PASSWORD': db_conf['password'],
        'HOST': db_conf['host'],
        'PORT': db_conf['port'],
    }

if "default" not in DATABASES:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }

# -----------------------------
# Password validation
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# Internationalization
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static files
# -----------------------------
STATIC_URL = 'static/'
STATIC_ROOT = CONFIG['server'].get('staticfiles', os.path.join(BASE_DIR, 'static'))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -----------------------------
# Default primary key
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# Redis + Channel Layers
# -----------------------------
REDIS_URL = CONFIG.get('channels', {}).get('redis_url', 'redis://127.0.0.1:6379/0')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

# -----------------------------
# ASGI server config
# -----------------------------
ASGI_HOST = CONFIG['server'].get('host', '0.0.0.0')
ASGI_PORT = int(CONFIG['server'].get('port', 8000))
ASGI_WORKERS = CONFIG['server'].get('workers', 1)  # untuk server, bukan modul

# -----------------------------
# Module-specific workers (Huey)
# -----------------------------
SERVER_WORKERS = CONFIG.get('workers', {})  # misal: {"authentication": {"workers": 1}}

# -----------------------------
# Logging
# -----------------------------
LOG_LEVEL = "DEBUG" if DEBUG else "WARNING"
LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"

try:
    import colorlog
    FORMATTERS = {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s" + LOG_FORMAT,
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "verbose": {"format": LOG_FORMAT},
    }
    COLOR_HANDLER = {"class": "logging.StreamHandler", "formatter": "color"}
except ImportError:
    FORMATTERS = {"verbose": {"format": LOG_FORMAT}}
    COLOR_HANDLER = {"class": "logging.StreamHandler", "formatter": "verbose"}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS,
    "handlers": {
        "console": COLOR_HANDLER,
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / f"{SERVICE_NAME}.log",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": LOG_LEVEL},
}

# -----------------------------
# Startup info
# -----------------------------
import logging
logger = logging.getLogger(__name__)
if DEBUG:
    logger.info("🚀 Running in DEBUG mode with verbose logging.")
else:
    logger.warning("⚙️ Running in PRODUCTION mode with minimal logging.")
