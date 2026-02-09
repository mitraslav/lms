# LMS (Learning Management System)

Проект LMS на Django + DRF с поддержкой фоновых задач Celery и деплоем через Docker Compose.

## Стек

- Django / DRF
- PostgreSQL
- Redis
- Celery + Celery Beat
- Nginx
- Docker + Docker Compose
- GitHub Actions (CI/CD)

---

# Локальный запуск через Docker Compose

## 1) Клонирование репозитория

```bash
git clone https://github.com/mitraslav/lms.git
cd lms
```

## 2) Подготовка переменных окружения

Скопируйте шаблон `.env_template` и заполните `.env`:

```bash
cp .env_template .env
```

Пример минимального `.env`:

```env
POSTGRES_DB=lms
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_password

DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Redis (Celery broker)
REDIS_HOST=redis
REDIS_PORT=6379
```

> Важно: файл `.env` не должен попадать в репозиторий.

## 3) Сборка и запуск всех сервисов

```bash
docker compose up --build
```

Запуск в фоне:

```bash
docker compose up --build -d
```

## 4) Проверка работоспособности

### Backend (Django)
Откройте в браузере:

- http://localhost/

Логи:

```bash
docker compose logs -f backend
```

### PostgreSQL

```bash
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "select 1;"
```

### Redis

```bash
docker compose exec redis redis-cli ping
```

### Celery worker

```bash
docker compose logs -f celery
```

### Celery Beat

```bash
docker compose logs -f celery_beat
```

---

# Полезные команды

### Миграции вручную

```bash
docker compose exec backend python manage.py migrate
```

### Создание суперпользователя

```bash
docker compose exec backend python manage.py createsuperuser
```

### Остановка контейнеров

```bash
docker compose down
```

### Остановка контейнеров + удаление томов (очистка БД)

```bash
docker compose down -v
```

---

# Контейнеры проекта

Проект разделён на отдельные контейнеры:

- `backend` — Django (gunicorn)
- `db` — PostgreSQL
- `redis` — Redis
- `celery` — Celery worker
- `celery_beat` — планировщик задач Celery Beat
- `nginx` — reverse proxy + раздача статики и медиа

Запуск и управление контейнерами выполняется через Docker Compose.

---

# CI/CD (GitHub Actions)

В репозитории настроен workflow GitHub Actions:

- запуск линтинга
- запуск тестов
- проверка сборки Docker-образов
- автоматический деплой на сервер через Docker Compose при пуше в ветку `develop`

Workflow расположен в:

```
.github/workflows/ci-cd.yml
```

---

# Деплой на сервер (Docker Compose)

Деплой выполняется автоматически через GitHub Actions по SSH.

## 1) Подготовка сервера

### Установить Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

### Установить Docker Compose plugin

```bash
sudo apt install -y docker-compose-plugin
```

Проверка:

```bash
docker --version
docker compose version
```

## 2) Открыть порты на сервере

Должны быть открыты:

- `22` (SSH)
- `80` (HTTP)

Если используется UFW:

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw enable
```

## 3) Развернуть проект на сервере

Создайте директорию и клонируйте репозиторий:

```bash
sudo mkdir -p /opt/apps
sudo chown $USER:$USER /opt/apps

cd /opt/apps
git clone https://github.com/mitraslav/lms.git
cd lms
```

## 4) Создать `.env` на сервере

На сервере нужно создать `.env`:

```bash
nano /opt/apps/lms/.env
```

Пример:

```env
POSTGRES_DB=lms
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_password

DJANGO_SECRET_KEY=super_secret_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your_server_ip,localhost,127.0.0.1

REDIS_HOST=redis
REDIS_PORT=6379
```

> Важно: `.env` хранится только на сервере и не коммитится в git.

## 5) Первый запуск вручную

Перед подключением CI/CD рекомендуется один раз поднять сервис вручную:

```bash
cd /opt/apps/lms
docker compose up -d --build
```

Проверка статуса:

```bash
docker compose ps
```

---

# Настройка GitHub Secrets (для деплоя)

Перейдите в GitHub репозитории:

**Settings → Secrets and variables → Actions → New repository secret**

Добавьте:

| Secret | Описание |
|--------|----------|
| `SERVER_HOST` | IP сервера |
| `SERVER_USER` | пользователь на сервере (например `ubuntu`) |
| `SERVER_PORT` | SSH порт (обычно `22`) |
| `SERVER_SSH_KEY` | приватный SSH ключ (id_rsa) |
| `SERVER_SSH_PASSPHRASE` | passphrase ключа (если есть) |
| `DJANGO_SECRET_KEY` | секретный ключ Django для CI |

---

# Как сдавать работу

Домашнее задание сдаётся ссылкой на Pull Request:

- изменения делаются в ветке домашней работы
- Pull Request открывается в ветку `develop`

---

# Адрес сервера

Развёрнутое приложение доступно по адресу:

**http://<IP_СЕРВЕРА>/**

(вставьте сюда реальный адрес после деплоя)
