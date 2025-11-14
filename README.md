# Backend

Fungsi utama Backend

1. Centralized core logic

2. Shared modules

3. Mempermudah maintainability

4. Mempermudah struktur proyek


# Clone Project:
```
git clone https://github.com/HKA-web/Backend.git
git submodule update --init --recursive
git pull --recurse-submodules
```

# Related Project:

1. Api Gateway: https://github.com/HKA-web/Api-Gateway.git
2. Whatsapp Bot: https://github.com/HKA-web/Whatsapp-Bot.git

# Instalation:

>Migrate Auth
```
cwd migrate auth
```
>Migrate <module>
```
cwd migrate
```
>Install Dependency Module
```
pip install -r <module>\requirements.txt --no-cache-dir
```
>Run Program
```
cwd runserver <host>:<port>
```

# Make Module:

1. Copy folder blank
2. ganti dengan nama module yang diinginkan
3. hapus semua folder dengan nama __pycache__ yang berada didalam module kamu, agar dibuatkan ulang oleh sistem saat dijalankan


# Commands
>Menjalankan server default port 8000
cwd runserver

>Menjalankan huey sebanyak 4 <optional>
cwd run_huey --workers 4
