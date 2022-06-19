# Задание на школу Бэкенд Разработки Яндекс

## Запуск проекта

Зависимости (python-пакеты) лежат в файле `products/requiremets.txt`

```shell
pip install -r app/requirements.txt
```

---
### Переменные окружения

При развертывании создайте в корне проекта файл с переменными окружения.
По умолчанию его название `.env`, но можно переопределить при запуске приложения

```shell
ENV_FILE=your_File.env python main.py
```

В этом файле объявите следующие переменные
```shell
POSTGRES_USER=user
POSTGRES_PASSWORD=passwd
POSTGRES_DB=backend
POSTGRES_HOST=database_host
POSTGRES_PORT=database_port

DEBUG=False
SERVER_NAME=Your Server Name
PROJECT_NAME="Backend School"

```

### Команды запуска

#### Uvicorn Way

Для запуска с помощью wsgi Uvicorn внутри папки `products` выполните

```shell
python main.py
```

или 

```shell
ENV_FILE=.env python main.py
```

#### Gunicorn Way

Для обработки большего числа запросов на одном сервере можно использовать
связку Gunicorn + Uvicorn для запуска через Gunicorn воркеров из Uvicorn'а.

```shell
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

#### Docker Compose Way

Перед запуском через Docker Compose также необходимо создать файл с переменными 
окружения `.env` или экспортировать их в среду. 

**ВАЖНО:** Для правильной работы в docker-compose без внешнего порта для БД, 
назначьте `POSTGRES_HOST=database`.

Для запуска проекта со всеми сервисами одновременно необходимо выполнить

```shell
docker-compose  up --build -d
```

---
### Миграции

Управление версиями БД осуществляется с помощью пакета `alembic`. 
#### Создание миграции
Для автоматического создания миграции при изменении схемы
нужно выполнить
```shell
alembic revision --autogenerate -m "Name of migration"
```
#### Применение миграций
Для обновления/инициализации таблиц через миграции выполните 
внутри папки `products` команду
```shell
alembic upgrade head
```