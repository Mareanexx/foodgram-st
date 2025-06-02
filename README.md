# Foodgram

## Описание проекта

Foodgram - это веб-приложение, которое позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а также скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Функциональность

- Регистрация и авторизация пользователей
- Создание, просмотр, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Подписка на других пользователей
- Формирование и скачивание списка покупок в PDF формате
- Админ-панель для управления пользователями и контентом

## Технологии

- Python 3.10
- Django 4.2
- Django REST framework
- PostgreSQL
- Docker
- Nginx
- GitHub Actions

## Запуск проекта

### Предварительные требования

- Docker
- Docker Compose

### Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Mareanexx/foodgram-st.git
cd foodgram-st
```

2. Создайте файл .env в корневой директории проекта.

3. Запустите проект через Docker Compose:
```bash
docker-compose up --build -d
```

4. После успешного запуска контейнеров, выполните миграции и загрузите тестовые данные:
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py load_ingredients
docker compose exec backend python manage.py load_test_data
```

### Доступ к проекту

После запуска проект будет доступен по следующим адресам:

- Веб-приложение: http://localhost:80
- API документация: http://localhost:80/api/docs/
- Админ-панель: http://localhost:80/admin/

### Тестовые пользователи

В проекте уже созданы тестовые пользователи:

- Email: masterchef@example.com (пароль: testpass123)
- Email: homecook@example.com (пароль: testpass123)
- Email: sweetbaker@example.com (пароль: testpass123)
- Email: foodlover@example.com (пароль: testpass123)
