# Backend Core

Fungsi utama Backend Core

1. Centralized core logic

2. Shared modules

3. Mempermudah maintainability

4. Mempermudah struktur proyek


# Clone Project:
```
git clone https://github.com/HKA-web/backend.git
git submodule update --init --recursive
git pull --recurse-submodules
```

# Related Project:

1. Api Gateway: https://github.com/HKA-web/Api-Gateway.gitss

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


# 🔑 List Commad:
```
Available subcommands:

[auth]
    changepassword
    createsuperuser

[channels]
    runworker

[contenttypes]
    remove_stale_contenttypes

[core]
    rundaphne
    runhuey
    runservice

[django]
    check
    compilemessages
    createcachetable
    dbshell
    diffsettings
    dumpdata
    flush
    inspectdb
    loaddata
    makemessages
    makemigrations
    migrate
    optimizemigration
    sendtestemail
    shell
    showmigrations
    sqlflush
    sqlmigrate
    sqlsequencereset
    squashmigrations
    startapp
    startproject
    test
    testserver

[rest_framework]
    generateschema

[sessions]
    clearsessions

[staticfiles]
    collectstatic
    findstatic
    runserver

Gunakan: cwd [command]
Contoh: cwd runserver, cwd runhuey authentication
```