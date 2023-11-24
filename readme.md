## SSRF уязвимость
Данный репозиторий содержит реализованную SSRF уязвимость, а так же одно из возможный решений по закрытию данной уязвимости.

### Настройка и запуск сервера (Ubuntu)
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

#### Запуск уязвимого сервера
```
$ uvicorn asgi_vunerable:app
```
#### Запуск сервера с исправленной SSRF-уязвимостью
```
$ uvicorn asgi:app
```