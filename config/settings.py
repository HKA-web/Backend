import os
import yaml
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Tentukan nama service saat run
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'users-service')

# Load YAML config
with open(BASE_DIR / 'config.yaml') as f:
    CONFIG = yaml.safe_load(f)
    
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG['server'].get('secret_key', 'django-insecure-$2of$_!*kpie7%j-runx!p=zf#uh($abdx%(-imd&h)v_o@oy4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG['server'].get('debug', True)

ALLOWED_HOSTS = CONFIG.get('allowed_hosts', ['*'])


# Application definition

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

ROOT_URLCONF = 'config.urls'

# Redis config
redis_conf = CONFIG.get('redis', {})
if redis_conf.get("enabled", False):
    REDIS_URL = f"redis://{redis_conf['host']}:{redis_conf['port']}/{redis_conf.get('db', 0)}"
    if redis_conf.get("password"):
        # tambahkan password ke URL
        REDIS_URL = f"redis://:{redis_conf['password']}@{redis_conf['host']}:{redis_conf['port']}/{redis_conf.get('db', 0)}"

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    # fallback ke dummy cache
    REDIS_URL = "redis://127.0.0.1:6379/0"
    CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }

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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

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

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Folder tujuan collectstatic
STATIC_ROOT = CONFIG['server'].get('staticfiles', os.path.join(BASE_DIR, 'static'))

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ASGI_APPLICATION = 'config.asgi.application'

