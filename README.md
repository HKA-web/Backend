# Backend Core

Fungsi utama Backend Core

1. Centralized core logic

- Semua fungsi microservice

2. Shared modules

- Bisa digunakan bersama oleh beberapa microservice:

	- sqlserver-service

3. Mempermudah maintainability

- Kalau ada perubahan di core, cukup update di satu tempat → semua service bisa pakai versi terbaru.

4. Mempermudah struktur proyek

- Jadi microservice nggak berantakan karena semua kode inti dipisah di satu folder.

## Clone Project:
```
git clone https://github.com/HKA-web/backend.git
git submodule update --init --recursive
git pull --recurse-submodules
```

# Arsitektur
```
                     +-------------------+
                     |   config.yaml     |
                     +-------------------+
                               |
                               v
               +---------------------------------+
               | Django Startup (manage.py runserver)
               +---------------------------------+
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
+-------------------------+                +--------------------------+
| Scan installed modules  |                | Independent modules      |
| apps.py.enabled == True |                | apps.py.enabled == False |
+-------------------------+                +--------------------------+
        |                                             |
        v                                             v
+-------------------------+                +--------------------------+
| Load into INSTALLED_APPS|                |  [NOT loaded]            |
| - Models                |                |  - No models              |
| - Views / URLs          |                |  - No urls                |
| - Signals               |                |  - No signals             |
+-------------------------+                +--------------------------+
        |
        v
+-------------------------+
| Run on default port     |
| (e.g., 8000 via runserver|
| or daphne in prod)      |
+-------------------------+

==========================================================

         Independent Module Execution (runservice)

      python manage.py runservice authentication --port 8001
                               |
                               v
                +-------------------------------+
                | Force-load apps.py.enabled==False
                +-------------------------------+
                               |
                               v
                +-------------------------------+
                | Dynamic URLs only for module  |
                | - authentication.urls         |
                +-------------------------------+
                               |
                               v
                +-------------------------------+
                | Run on its own port           |
                | (e.g., 8001)                  |
                +-------------------------------+

```

## 🔑 Daftar Perintah:

1. python manage.py runserver atau python manage.py runserver --port 8001

2. python manage.py runservice <module> atau python manage.py runservice <module> --port 8001

3. python manage.py runhuey <module> atau python manage.py runhuey <module> --port 8001

4. python manage.py runhuey shell