#!/usr/bin/env python
import os
import sys
from django.conf import settings

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Pastikan Django terinstal.") from exc

    host = getattr(settings, "SERVER_HOST", "127.0.0.1")
    port = getattr(settings, "SERVER_PORT", "8000")

    if len(sys.argv) == 2 and sys.argv[1] == 'runserver':
        sys.argv.append(f"{host}:{port}")
    elif len(sys.argv) == 1:
        sys.argv = ['manage.py', 'runserver', f"{host}:{port}"]
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
