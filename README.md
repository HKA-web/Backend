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