# 🚀 Career Intelligence Platform

**AI-powered career consulting and HR management platform**

Профессиональная платформа для карьерного консультирования на базе Google Gemini 2.5 Pro, психографического анализа (PGD) и обработки резюме.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![React](https://img.shields.io/badge/React-18.2-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)

---

## 📋 О проекте

Career Intelligence Platform — это современный сервис для:
- 🧠 **Психографического анализа личности** (PGD-матрица)
- 📄 **Обработки резюме** (PDF, DOCX, TXT)
- 🤖 **AI-консультирования** через Google Gemini 2.5 Pro
- 📊 **Оценки soft/hard skills** с визуализацией
- 🎯 **Карьерных рекомендаций** с matching score
- 💼 **HR-аналитики** для подбора персонала

### Ключевые возможности

✅ **Полный стек:** FastAPI (async) + React (TypeScript) + PostgreSQL
✅ **AI-анализ:** Интеграция с Gemini 2.5 Pro для глубоких рекомендаций
✅ **PGD-матрица:** Психографический профиль на основе даты рождения
✅ **Парсинг резюме:** Автоматическое извлечение навыков и опыта
✅ **Визуализация:** Интерактивные графики (Recharts)
✅ **JWT аутентификация:** Безопасный доступ к персональным данным
✅ **Async архитектура:** Высокая производительность и масштабируемость
✅ **Production-ready:** Docker, PostgreSQL, полная документация API

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  Login/Register │ Dashboard │ File Upload │ Analysis View   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────┴────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │   Auth   │  │  Documents  │  │      Analysis        │   │
│  │ (JWT)    │  │  (Upload)   │  │  (PGD + AI)          │   │
│  └──────────┘  └─────────────┘  └──────────────────────┘   │
│         │              │                   │                 │
│    ┌────┴──────────────┴───────────────────┴────┐           │
│    │           Services Layer                    │           │
│    │  • PGD Calculator                           │           │
│    │  • Document Processor (PDF/DOCX parsing)    │           │
│    │  • AI Service (Gemini integration)          │           │
│    └─────────────────┬───────────────────────────┘           │
└──────────────────────┼─────────────────────────────────────┘
                       │
        ┌──────────────┴───────────────┬──────────────────┐
        │                              │                  │
  ┌─────▼──────┐              ┌────────▼────────┐  ┌─────▼─────┐
  │ PostgreSQL │              │  Google Gemini  │  │  File     │
  │  Database  │              │    2.5 Pro      │  │  Storage  │
  └────────────┘              └─────────────────┘  └───────────┘
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Google Gemini API Key ([получить здесь](https://ai.google.dev/))

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/career-intelligence-platform.git
cd career-intelligence-platform
```

### 2. Backend setup

```bash
cd backend

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env и добавьте ваши ключи

# Запустите сервер
uvicorn main:app --reload
```

Backend будет доступен на `http://localhost:8000`
API документация: `http://localhost:8000/docs`

### 3. Frontend setup

```bash
cd ../frontend

# Установите зависимости
npm install

# Настройте переменные окружения
cp .env.example .env
# Добавьте: VITE_API_URL=http://localhost:8000

# Запустите dev server
npm run dev
```

Frontend будет доступен на `http://localhost:3000`

### 4. Docker (альтернативный способ)

```bash
cd backend
docker-compose up -d
```

Это запустит:
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Frontend: соберите отдельно

---

## 📚 API Documentation

### Authentication

#### POST `/api/v1/auth/register`
Регистрация нового пользователя

**Request:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123",
  "full_name": "Иван Иванов",
  "date_of_birth": "15.05.1990",
  "gender": "М"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Иван Иванов"
  }
}
```

#### POST `/api/v1/auth/login`
Вход в систему

### Documents

#### POST `/api/v1/documents/upload`
Загрузка резюме (PDF, DOCX, TXT)

**Request:** `multipart/form-data` с полем `file`

**Response:**
```json
{
  "id": 1,
  "filename": "resume.pdf",
  "file_type": "pdf",
  "file_size": 524288,
  "extracted_skills": {
    "hard_skills": ["Python", "React", "PostgreSQL"],
    "soft_skills": ["Leadership", "Communication", "Problem Solving"]
  },
  "uploaded_at": "2026-02-23T10:30:00Z"
}
```

#### GET `/api/v1/documents/`
Список всех документов пользователя

### Analysis

#### POST `/api/v1/analysis/create`
Создать карьерный анализ

**Request:**
```json
{
  "include_documents": true
}
```

**Response:**
```json
{
  "id": 1,
  "pgd_data": {
    "main_cup": {"A": 15, "B": 5, "V": 8, ...},
    "ancestral_data": {...},
    "crossroads": {...}
  },
  "ai_analysis": "Глубокий анализ личности...",
  "career_tracks": [
    {
      "title": "Software Architect",
      "description": "Ведущий архитектор программного обеспечения",
      "match_score": 92,
      "key_strengths": ["Системное мышление", "Технические навыки"],
      "development_areas": ["Публичные выступления", "Делегирование"]
    }
  ],
  "skills_breakdown": {
    "soft_skills": ["Leadership", "Communication"],
    "hard_skills": ["Python", "React", "PostgreSQL"],
    "soft_skills_score": 75,
    "hard_skills_score": 85,
    "balance_ratio": "47/53"
  },
  "created_at": "2026-02-23T10:35:00Z"
}
```

#### GET `/api/v1/analysis/{id}`
Получить анализ по ID

Полная документация: `http://localhost:8000/docs`

---

## 🎨 Frontend Pages

### 1. Login Page (`/login`)
- Email/password аутентификация
- Валидация форм
- Error handling

### 2. Register Page (`/register`)
- Регистрация с PGD данными
- Валидация даты рождения (DD.MM.YYYY)
- Выбор пола (М/Ж)

### 3. Dashboard (`/dashboard`)
- Drag & drop загрузка файлов
- Отображение загруженных документов
- Кнопка запуска AI-анализа
- История анализов

### 4. Analysis Page (`/analysis/:id`)
- Визуализация soft/hard skills (Pie Chart)
- Карьерные треки с match scores
- Полный текстовый анализ
- Экспорт в TXT

### 5. History Page (`/history`)
- Список всех анализов
- Дата и время создания
- Быстрый доступ к результатам

---

## 🧪 Тестирование

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

---

## 🛠️ Технологии

### Backend
- **FastAPI** — современный async веб-фреймворк
- **SQLAlchemy** — ORM для работы с БД
- **PostgreSQL** — реляционная база данных
- **Google Generative AI** — интеграция с Gemini
- **PyPDF2 / python-docx** — парсинг документов
- **Pydantic** — валидация данных
- **JWT (python-jose)** — аутентификация
- **Uvicorn** — ASGI сервер

### Frontend
- **React 18** — UI библиотека
- **TypeScript** — статическая типизация
- **Vite** — быстрый сборщик
- **Tailwind CSS** — utility-first CSS
- **Zustand** — state management
- **Axios** — HTTP клиент
- **Recharts** — визуализация данных
- **React Dropzone** — drag & drop upload

---

## 📁 Структура проекта

```
career-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # Эндпоинты аутентификации
│   │   │   │   ├── documents.py     # Загрузка документов
│   │   │   │   └── analysis.py      # Карьерный анализ
│   │   │   └── dependencies.py      # Общие зависимости
│   │   ├── core/
│   │   │   ├── config.py            # Конфигурация приложения
│   │   │   ├── database.py          # Подключение к БД
│   │   │   └── security.py          # JWT и хеширование
│   │   ├── models/
│   │   │   ├── models.py            # SQLAlchemy модели
│   │   │   └── schemas.py           # Pydantic схемы
│   │   ├── services/
│   │   │   ├── pgd_service.py       # PGD расчёты
│   │   │   ├── document_service.py  # Парсинг файлов
│   │   │   └── ai_service.py        # Gemini интеграция
│   │   └── utils/
│   ├── main.py                      # Точка входа FastAPI
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/              # Переиспользуемые компоненты
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── AnalysisPage.tsx
│   │   │   └── HistoryPage.tsx
│   │   ├── services/
│   │   │   └── api.ts               # API клиент
│   │   ├── stores/
│   │   │   └── authStore.ts         # Zustand store
│   │   ├── types/
│   │   │   └── api.ts               # TypeScript типы
│   │   ├── App.tsx                  # Главный компонент
│   │   ├── main.tsx                 # Точка входа
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── deployment/
│   └── render.yaml                  # Render Blueprint
├── DEPLOYMENT.md                    # Инструкция по деплою
└── README.md                        # Этот файл
```

---

## 🌐 Деплой на Render

Подробная инструкция: [DEPLOYMENT.md](./DEPLOYMENT.md)

### Быстрый деплой

1. Загрузите проект на GitHub
2. Создайте Blueprint на Render
3. Добавьте `GOOGLE_API_KEY` в environment variables
4. Render автоматически развернет все сервисы

**Необходимые сервисы:**
- PostgreSQL Database
- Backend Web Service
- Frontend Static Site

---

## 🔧 Конфигурация

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/career_intelligence

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini
GOOGLE_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-2.5-pro

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,docx,txt
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

---

## 📝 Примеры использования

### 1. Создание анализа через API

```python
import requests

# Регистрация
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Тест Тестов",
    "date_of_birth": "15.05.1990",
    "gender": "М"
})
tokens = response.json()

# Загрузка резюме
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
files = {"file": open("resume.pdf", "rb")}
response = requests.post("http://localhost:8000/api/v1/documents/upload", 
                        headers=headers, files=files)

# Создание анализа
response = requests.post("http://localhost:8000/api/v1/analysis/create",
                        headers=headers, json={"include_documents": True})
analysis = response.json()
print(f"Match score: {analysis['career_tracks'][0]['match_score']}%")
```

### 2. PGD расчёты (standalone)

```python
from backend.app.services.pgd_service import PGDCalculator

calculator = PGDCalculator(
    name="Иван Иванов",
    date="15.05.1990",
    sex="М"
)

result = calculator.get_full_analysis()
print(f"Точка А: {result['main_cup']['A']}")
print(f"Карма рода: {result['tasks']['karma_of_genus']}")
```

---

## 🤝 Contributing

Мы приветствуем вклад в проект!

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

---

## 👥 Авторы

- **Original PGD Algorithm** — annamistery
- **AI Integration & Full Stack** — [Your Name]

---

## 🙏 Благодарности

- [Google Gemini](https://ai.google.dev/) — AI-powered анализ
- [FastAPI](https://fastapi.tiangolo.com/) — отличный фреймворк
- [React](https://react.dev/) — современная UI библиотека
- [Render](https://render.com/) — простой deployment

---

## 📞 Контакты

- Email: support@example.com
- Telegram: @yourusername
- Website: https://career-intelligence.com

---

## 🗺️ Roadmap

### Версия 1.1 (Q2 2026)
- [ ] Парная диагностика (совместимость с партнёром)
- [ ] Экспорт в PDF с дизайном
- [ ] Интеграция с LinkedIn API
- [ ] Рекомендации вакансий

### Версия 1.2 (Q3 2026)
- [ ] HR-панель для рекрутеров
- [ ] Matching кандидатов с вакансиями
- [ ] Team compatibility анализ
- [ ] Advanced analytics dashboard

### Версия 2.0 (Q4 2026)
- [ ] Мобильные приложения (iOS/Android)
- [ ] Видео-консультации с AI
- [ ] Интеграция с HR-системами (SAP, Workday)
- [ ] Marketplace для консультантов

---

**Made with ❤️ and AI**
