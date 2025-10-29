import os
import sys
import yaml
import logging
import platform
import structlog
from pathlib import Path
from django.utils.log import RequireDebugTrue

# === BASE PATH SETUP ===========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / "apps"

for path in (BASE_DIR, APPS_DIR):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# === AUTO SCAN APP =============================================================
AUTO_APPS = []
if APPS_DIR.exists():
    for app in APPS_DIR.iterdir():
        if app.is_dir() and (app / "__init__.py").exists():
            AUTO_APPS.append(app.name)

for app in BASE_DIR.iterdir():
    if app.is_dir() and (app / "__init__.py").exists():
        if app.name not in AUTO_APPS and app.name not in ["config", "apps", "__pycache__"]:
            AUTO_APPS.append(app.name)

# === CLEAR TERMINAL DAN LIST APP ==============================================
if os.environ.get("RUN_MAIN") == "true":
    os.system("cls" if platform.system() == "Windows" else "clear")
    print("\n Django Auto App Scanner\n" + "=" * 35)
    for i, app in enumerate(AUTO_APPS, start=1):
        print(f"  {i:02d}. {app}")
    print("=" * 35)
    print(f" Total {len(AUTO_APPS)} app terdeteksi.\n")

# === LOAD CONFIG YAML ==========================================================
CONFIG_PATH = BASE_DIR / "config.yaml"
CONFIG = {}

if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            CONFIG = yaml.safe_load(f) or {}
            print("[INFO] config.yaml loaded successfully.")
    except Exception as e:
        print(f"[WARN] Gagal membaca config.yaml: {e}")
else:
    print("[WARN] config.yaml tidak ditemukan, menggunakan default setting.")

# === DJANGO CORE SETTINGS ======================================================
SECRET_KEY = CONFIG.get("secret_key", "django-insecure-xs_%_86*c_@y&wj+d3sswr_l2e-x8p@ewp-sety*f&gv+6hg__")
DEBUG = CONFIG.get("debug", True)
ALLOWED_HOSTS = CONFIG.get("allowed_hosts", ["*"])

# === APLIKASI ==================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    *AUTO_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# === DATABASE ==================================================================
DATABASES = {}

for alias, db_conf in CONFIG.get("databases", {}).items():
    # ubah semua key menjadi lowercase
    db_conf = {k.lower(): v for k, v in db_conf.items()}

    if 'engine' in db_conf:
        DATABASES[alias] = {
            'ENGINE': db_conf.get('engine', 'django.db.backends.sqlite3'),
            'NAME': db_conf.get('name', os.path.join(BASE_DIR, 'db.sqlite3')),
            'USER': db_conf.get('user', ''),
            'PASSWORD': db_conf.get('password', ''),
            'HOST': db_conf.get('host', 'localhost'),
            'PORT': db_conf.get('port', ''),
        }

if "default" not in DATABASES:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "111111",
        "HOST": "localhost",
        "PORT": "5432",
        "OPTIONS": {"options": "-c search_path=public"},
    }

SQLSERVER_DEFAULT = CONFIG.get('databases', {}).get('sqlserver', {})
if not SQLSERVER_DEFAULT:
    SQLSERVER_DEFAULT = {
        "server1": {
            "driver": "{SQL Server}",
            "pipe": r"\\192.168.6.28\pipe\sql\query",
            "database": "master",
            "uid": "sa",
            "pwd": "PASSWORDSETUPSRVNUSANTARAMUJUR",
        }
    }
    
# === VALIDATION & LOCALE =======================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = CONFIG.get("language_code", "en-us")
TIME_ZONE = CONFIG.get("time_zone", "UTC")
USE_I18N = True
USE_TZ = True

# === STATIC FILES ==============================================================
STATIC_URL = CONFIG.get("static_url", "static/")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === STRUCTLOG (Colored Logging) ===============================================
RESET = "\033[0m"
COLORS = {
    "DEBUG": "\033[34m",     # blue
    "INFO": "\033[32m",      # green
    "WARNING": "\033[33m",   # yellow
    "ERROR": "\033[31m",     # red
    "CRITICAL": "\033[35m",  # magenta
    "SQL": "\033[36m",       # cyan
}

class ColoredConsoleRenderer(structlog.dev.ConsoleRenderer):
    def __call__(self, logger, name, event_dict):
        level = event_dict.get("level", "INFO").upper()
        msg = event_dict.get("event", "")
        logger_name = event_dict.get("logger", "")
        color = COLORS.get(level, RESET)

        if "django.db.backends" in logger_name or "SELECT" in msg:
            level = "SQL"
            color = COLORS["SQL"]

        formatted = f"{color}[{level:<7}] {logger_name:<30} | {msg}{RESET}"
        return formatted

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.UnicodeDecoder(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    logger_factory=structlog.stdlib.LoggerFactory(),
)

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": ColoredConsoleRenderer(),
                "foreign_pre_chain": [
                    structlog.processors.TimeStamper(fmt="%H:%M:%S"),
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                ],
            },
        },
        "filters": {"require_debug_true": {"()": RequireDebugTrue}},
        "handlers": {
            "console": {
                "level": "DEBUG",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
        },
        "loggers": {
            "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
            "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
            "django.db.backends": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        },
    }
