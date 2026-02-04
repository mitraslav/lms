## Запуск через Docker Compose

### 1) Подготовка переменных окружения
Скопируйте шаблон и заполните значения:
```bash
cp .env_template .env
```
### 2) Сборка и запуск всех сервисов
```
docker compose up --build
```
Если фоном:
```
docker compose up --build -d
```
### 3) Проверка работоспособности сервисов Backend (Django)

- Откройте: http://localhost:8000/
- Логи:
```
docker compose logs -f backend
```
PostgreSQL
```
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "select 1;"
```
Redis
```
docker compose exec redis redis-cli ping
```
Celery worker
```
docker compose logs -f celery
```
Celery Beat
```
docker compose logs -f celery_beat
```

### Полезные команды
#### Миграции вручную:
```
docker compose exec backend python manage.py migrate
```
#### Создать суперпользователя:
```
docker compose exec backend python manage.py createsuperuser
```
#### Остановить и удалить контейнеры:
```
docker compose down
```
#### Остановить и удалить + тома БД:
```
docker compose down -v
```

