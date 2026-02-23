# 🚀 Career Intelligence Platform - Deployment Guide for Render

Полная инструкция по развертыванию платформы карьерного консультирования на Render.com

---

## 📋 Структура проекта

```
career-intelligence-platform/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── documents.py
│   │   │   │   └── analysis.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── pgd_service.py
│   │   │   ├── document_service.py
│   │   │   └── ai_service.py
│   │   └── utils/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
└── deployment/
    └── render.yaml
```

---

## 🛠️ Предварительные требования

1. **Аккаунт на Render.com**
   - Зарегистрируйтесь на https://render.com

2. **Google Gemini API Key**
   - Получите ключ: https://ai.google.dev/
   - Сохраните API_KEY

3. **Git Repository**
   - Загрузите проект на GitHub/GitLab

---

## 🔧 Шаг 1: Подготовка локального окружения

### 1.1 Backend (локальная разработка)

```bash
cd backend

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp .env.example .env

# Отредактируйте .env:
nano .env
```

Минимальные переменные для .env:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/career_intelligence
SECRET_KEY=your-super-secret-key-min-32-chars
GOOGLE_API_KEY=your-google-gemini-api-key
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### 1.2 Frontend (локальная разработка)

```bash
cd frontend

# Установите зависимости
npm install

# Создайте .env файл
cp .env.example .env

# Отредактируйте .env:
echo "VITE_API_URL=http://localhost:8000" > .env

# Запустите dev server
npm run dev
```

### 1.3 Локальный запуск с Docker

```bash
# В корне проекта
cd backend

# Запустите Docker Compose
docker-compose up -d

# Backend будет на http://localhost:8000
# Docs на http://localhost:8000/docs
```

---

## ☁️ Шаг 2: Деплой на Render

### Метод 1: Через Render Blueprint (Рекомендуется)

1. **Загрузите проект на GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/career-intelligence-platform.git
   git push -u origin main
   ```

2. **Создайте новый Blueprint на Render**
   - Перейдите на https://dashboard.render.com/
   - Нажмите "New" → "Blueprint"
   - Подключите GitHub репозиторий
   - Render автоматически найдет `deployment/render.yaml`

3. **Настройте Environment Variables**
   - Database создастся автоматически
   - **ОБЯЗАТЕЛЬНО** добавьте `GOOGLE_API_KEY` в настройках backend сервиса
   - Обновите `BACKEND_CORS_ORIGINS` после создания frontend URL

4. **Деплой**
   - Render автоматически развернет все сервисы
   - Ожидайте 5-10 минут для первого деплоя

### Метод 2: Ручное создание сервисов

#### 2.1 Создайте PostgreSQL Database

1. Dashboard → "New" → "PostgreSQL"
2. Настройки:
   - Name: `career-intelligence-db`
   - Database: `career_intelligence`
   - User: `career_user`
   - Region: выберите ближайший
   - Plan: Starter (Free)

3. Сохраните Internal Database URL (формат: `postgresql://...`)

#### 2.2 Создайте Backend Web Service

1. Dashboard → "New" → "Web Service"
2. Подключите GitHub репозиторий
3. Настройки:
   - Name: `career-intelligence-backend`
   - Region: тот же, что и БД
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Environment Variables:
   ```
   DATABASE_URL=<Internal Database URL from step 2.1>
   SECRET_KEY=<generate-random-32-char-string>
   GOOGLE_API_KEY=<your-gemini-api-key>
   GEMINI_MODEL=gemini-2.5-pro
   BACKEND_CORS_ORIGINS=["https://your-frontend-url.onrender.com"]
   PYTHON_VERSION=3.11
   ```

5. Advanced → Health Check Path: `/health`

6. Create Web Service

#### 2.3 Создайте Frontend Static Site

1. Dashboard → "New" → "Static Site"
2. Подключите тот же GitHub репозиторий
3. Настройки:
   - Name: `career-intelligence-frontend`
   - Branch: `main`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

4. Environment Variables:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```
   (Замените URL после создания backend)

5. Rewrite Rules (для React Router):
   - Source: `/*`
   - Destination: `/index.html`
   - Action: Rewrite

6. Create Static Site

#### 2.4 Обновите CORS

После создания фронтенда:
1. Скопируйте URL frontend (например: `https://career-intelligence-frontend.onrender.com`)
2. Перейдите в настройки backend сервиса
3. Обновите `BACKEND_CORS_ORIGINS`:
   ```
   BACKEND_CORS_ORIGINS=["https://career-intelligence-frontend.onrender.com"]
   ```
4. Сохраните и перезапустите backend

---

## 🧪 Шаг 3: Проверка работы

### 3.1 Backend Health Check

```bash
curl https://your-backend-url.onrender.com/health
# Ответ: {"status":"healthy"}
```

### 3.2 API Documentation

Откройте в браузере:
```
https://your-backend-url.onrender.com/docs
```

Вы должны увидеть Swagger UI с документацией API.

### 3.3 Тест регистрации

1. Откройте frontend URL в браузере
2. Нажмите "Зарегистрироваться"
3. Заполните форму:
   - Email: test@example.com
   - Пароль: testpassword123
   - Имя: Тест Тестов
   - Дата рождения: 15.05.1990
   - Пол: Мужской
4. Нажмите "Зарегистрироваться"
5. Если успешно → вы попадете на Dashboard

### 3.4 Тест загрузки резюме

1. На Dashboard перетащите PDF/DOCX файл
2. Дождитесь завершения загрузки
3. Проверьте, что отображаются извлеченные навыки

### 3.5 Тест AI-анализа

1. После загрузки резюме нажмите "Запустить анализ"
2. Ожидайте 30-60 секунд
3. Должны открыться результаты с:
   - Графиками soft/hard skills
   - Карьерными треками
   - Полным текстовым анализом

---

## 🔑 Важные переменные окружения

### Backend (.env)

| Переменная | Обязательна | Описание | Пример |
|-----------|-------------|----------|--------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | ✅ | JWT encryption key (32+ chars) | `your-super-secret-key-min-32-chars` |
| `GOOGLE_API_KEY` | ✅ | Google Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL` | ❌ | Gemini model name | `gemini-2.5-pro` (default) |
| `BACKEND_CORS_ORIGINS` | ✅ | Frontend URLs for CORS | `["https://frontend.com"]` |
| `MAX_UPLOAD_SIZE` | ❌ | Max file size in bytes | `10485760` (10MB, default) |

### Frontend (.env)

| Переменная | Обязательна | Описание | Пример |
|-----------|-------------|----------|--------|
| `VITE_API_URL` | ✅ | Backend API URL | `https://backend.onrender.com` |

---

## 📊 Мониторинг и логи

### Просмотр логов на Render

1. Dashboard → Выберите сервис
2. Перейдите во вкладку "Logs"
3. В реальном времени отображаются:
   - Запросы к API
   - Ошибки
   - Статус задач

### Важные логи для отладки

**Backend:**
```
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: "POST /api/v1/auth/register HTTP/1.1" 201
INFO: Sending request to Gemini API...
INFO: Successfully received analysis from Gemini
```

**Ошибки:**
```
ERROR: Could not validate credentials (401) - проверьте JWT токен
ERROR: Failed to process document - проблема с парсингом файла
ERROR: Error generating analysis - проблема с Gemini API
```

---

## 🐛 Решение проблем (Troubleshooting)

### Проблема 1: Backend не запускается

**Симптомы:**
```
ERROR: Could not connect to database
```

**Решение:**
1. Проверьте формат `DATABASE_URL`:
   ```
   postgresql+asyncpg://user:password@hostname:5432/dbname
   ```
2. Убедитесь, что БД создана и доступна
3. Render БД URL формат: `postgresql://...` → поменяйте на `postgresql+asyncpg://...`

### Проблема 2: CORS ошибки

**Симптомы:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Решение:**
1. В настройках backend добавьте frontend URL в `BACKEND_CORS_ORIGINS`
2. Формат должен быть JSON array: `["https://frontend.onrender.com"]`
3. Перезапустите backend сервис

### Проблема 3: Gemini API errors

**Симптомы:**
```
ERROR: Error generating analysis: 401 Unauthorized
```

**Решение:**
1. Проверьте валидность `GOOGLE_API_KEY`
2. Убедитесь, что API key активирован для Gemini API
3. Проверьте квоты: https://console.cloud.google.com/

### Проблема 4: Frontend не отображается

**Симптомы:**
- Пустая страница
- 404 на маршрутах

**Решение:**
1. Проверьте Rewrite Rules:
   - Source: `/*`
   - Destination: `/index.html`
2. Убедитесь, что `VITE_API_URL` указывает на правильный backend URL
3. Пересоберите frontend: Environment → Manual Deploy → Clear build cache & deploy

### Проблема 5: File upload fails

**Симптомы:**
```
File too large or File type not allowed
```

**Решение:**
1. Проверьте размер файла (по умолчанию лимит 10MB)
2. Поддерживаемые форматы: PDF, DOCX, TXT
3. Увеличьте `MAX_UPLOAD_SIZE` в backend env vars (в байтах)

---

## 🔐 Безопасность

### Обязательные меры

1. **SECRET_KEY**
   - Генерируйте криптографически стойкий ключ:
     ```python
     import secrets
     print(secrets.token_urlsafe(32))
     ```
   - НЕ используйте одинаковый ключ для dev и production

2. **HTTPS Only**
   - Render автоматически предоставляет SSL
   - Убедитесь, что все URLs используют `https://`

3. **Environment Variables**
   - Никогда не коммитьте `.env` файлы в Git
   - Используйте `.env.example` как шаблон

4. **Database**
   - Используйте сильные пароли
   - Render PostgreSQL защищен по умолчанию

5. **Rate Limiting**
   - Рассмотрите добавление rate limiting middleware
   - Пример в `main.py`:
     ```python
     from slowapi import Limiter
     limiter = Limiter(key_func=get_remote_address)
     app.state.limiter = limiter
     ```

---

## 📈 Масштабирование

### Обновление планов на Render

**Free Tier (Starter):**
- Backend: 512MB RAM, спит после 15 мин неактивности
- Database: 1GB storage
- Frontend: безлимитная пропускная способность

**Paid Tier (Starter+):**
- Backend: 1GB+ RAM, всегда активен
- Database: 10GB+ storage
- Улучшенная производительность

**Переход на Paid:**
1. Dashboard → Сервис → Settings → Plan
2. Выберите нужный план
3. Подтвердите оплату

### Horizontal Scaling

Для высоких нагрузок:
1. Используйте Render Auto-Scaling
2. Добавьте Redis для кэширования:
   - Активируйте `ENABLE_CACHE=True`
   - Подключите Redis instance
3. Используйте CDN для статики (Cloudflare)

---

## 🎯 Best Practices

1. **Git Workflow**
   ```bash
   # Создайте feature branch
   git checkout -b feature/new-feature
   
   # После изменений
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   
   # Создайте Pull Request
   # После merge в main → Render автоматически задеплоит
   ```

2. **Database Migrations**
   ```bash
   # В backend директории
   alembic init migrations
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

3. **Мониторинг**
   - Настройте уведомления в Render (Settings → Notifications)
   - Добавьте health check endpoints
   - Используйте Sentry для error tracking

4. **Бэкапы**
   - Render автоматически создает бэкапы БД (Paid plans)
   - Экспортируйте важные данные регулярно:
     ```bash
     pg_dump $DATABASE_URL > backup.sql
     ```

---

## 📝 Дополнительные команды

### Backend

```bash
# Запуск локально
uvicorn main:app --reload --port 8000

# Тестирование
pytest

# Форматирование кода
black .
isort .

# Линтинг
flake8 app/
mypy app/
```

### Frontend

```bash
# Development
npm run dev

# Production build
npm run build

# Preview build
npm run preview

# Линтинг
npm run lint
```

---

## 🆘 Поддержка

**Проблемы с проектом:**
- GitHub Issues: https://github.com/yourusername/career-intelligence-platform/issues

**Проблемы с Render:**
- Render Docs: https://render.com/docs
- Support: https://render.com/support

**Проблемы с Gemini API:**
- Google AI Docs: https://ai.google.dev/docs
- Support: https://support.google.com/

---

## ✅ Чеклист успешного деплоя

- [ ] GitHub репозиторий создан и загружен
- [ ] PostgreSQL база данных создана на Render
- [ ] Backend сервис создан и запущен
- [ ] Frontend сайт создан и задеплоен
- [ ] `GOOGLE_API_KEY` добавлен в backend env vars
- [ ] `BACKEND_CORS_ORIGINS` обновлен с frontend URL
- [ ] `VITE_API_URL` в frontend указывает на backend URL
- [ ] Health check работает: `/health` → `{"status":"healthy"}`
- [ ] API docs доступны: `/docs`
- [ ] Регистрация нового пользователя работает
- [ ] Загрузка файлов работает
- [ ] AI-анализ генерируется успешно
- [ ] Все ссылки используют HTTPS

---

## 🎉 Готово!

Ваша платформа Career Intelligence готова к использованию!

**Frontend URL:** `https://your-app.onrender.com`
**Backend API:** `https://your-api.onrender.com`
**API Docs:** `https://your-api.onrender.com/docs`

---

**Версия документа:** 1.0
**Последнее обновление:** 2026-02-23
