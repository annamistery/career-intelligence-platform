# 📦 Полный список файлов Career Intelligence Platform

## Backend (FastAPI)

### Корневая директория backend/
```
backend/
├── main.py                          # Точка входа приложения FastAPI
├── requirements.txt                 # Python зависимости
├── Dockerfile                       # Docker конфигурация
├── docker-compose.yml               # Docker Compose для локальной разработки
├── .env.example                     # Шаблон переменных окружения
├── .gitignore                       # Git ignore файл
└── README.md                        # Backend документация
```

### app/ (основное приложение)
```
app/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── dependencies.py              # JWT auth dependency
│   └── endpoints/
│       ├── __init__.py
│       ├── auth.py                  # Регистрация, вход, refresh token
│       ├── documents.py             # Загрузка, список, удаление документов
│       └── analysis.py              # PGD расчёты, AI-анализ, история
├── core/
│   ├── __init__.py
│   ├── config.py                    # Настройки через Pydantic Settings
│   ├── database.py                  # Async SQLAlchemy setup
│   └── security.py                  # JWT, password hashing
├── models/
│   ├── __init__.py
│   ├── models.py                    # SQLAlchemy ORM модели (User, Document, Analysis)
│   └── schemas.py                   # Pydantic схемы для валидации
├── services/
│   ├── __init__.py
│   ├── pgd_service.py               # PGD расчёты (рефакторинг pgd_bot.py)
│   ├── document_service.py          # Парсинг PDF/DOCX/TXT, извлечение навыков
│   └── ai_service.py                # Интеграция с Google Gemini 2.5 Pro
└── utils/
    └── __init__.py
```

---

## Frontend (React + TypeScript)

### Корневая директория frontend/
```
frontend/
├── index.html                       # HTML шаблон
├── package.json                     # NPM зависимости
├── tsconfig.json                    # TypeScript конфигурация
├── vite.config.ts                   # Vite сборщик
├── tailwind.config.js               # Tailwind CSS конфигурация
├── postcss.config.js                # PostCSS конфигурация
├── Dockerfile                       # Docker конфигурация
├── nginx.conf                       # Nginx для production
├── .env.example                     # Шаблон переменных окружения
├── .gitignore                       # Git ignore файл
└── README.md                        # Frontend документация
```

### src/ (исходный код)
```
src/
├── main.tsx                         # Точка входа React
├── App.tsx                          # Главный компонент с роутингом
├── index.css                        # Глобальные стили (Tailwind)
├── vite-env.d.ts                    # Vite типы
├── components/                      # Переиспользуемые компоненты
│   └── (пустая, можно добавить UI компоненты)
├── pages/                           # Страницы приложения
│   ├── LoginPage.tsx                # Страница входа
│   ├── RegisterPage.tsx             # Страница регистрации
│   ├── DashboardPage.tsx            # Главный дашборд
│   ├── AnalysisPage.tsx             # Просмотр результатов анализа
│   └── HistoryPage.tsx              # История анализов
├── services/                        # API сервисы
│   └── api.ts                       # Axios клиент с JWT interceptors
├── stores/                          # State management
│   └── authStore.ts                 # Zustand store для аутентификации
├── types/                           # TypeScript типы
│   └── api.ts                       # Типы для API responses
└── utils/                           # Утилиты
    └── (пустая, можно добавить helpers)
```

---

## Deployment

### deployment/
```
deployment/
├── render.yaml                      # Render Blueprint (автоматический деплой)
└── README.md                        # Дополнительная информация
```

---

## Корень проекта
```
career-intelligence-platform/
├── README.md                        # Основная документация
├── DEPLOYMENT.md                    # Подробная инструкция по деплою
├── LICENSE                          # MIT License
├── .gitignore                       # Глобальный gitignore
└── docs/                            # Дополнительная документация
    ├── API.md                       # API документация
    ├── ARCHITECTURE.md              # Архитектура проекта
    └── CONTRIBUTING.md              # Гайд для контрибьюторов
```

---

## Файлы для создания вручную

### Backend дополнительные файлы (опционально)

1. **backend/.gitignore**
```
__pycache__/
*.py[cod]
*$py.class
.env
.venv
venv/
env/
ENV/
uploads/
reports/
*.log
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
```

2. **backend/pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

3. **backend/alembic.ini** (для миграций БД)
```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/db
```

### Frontend дополнительные файлы (опционально)

1. **frontend/.gitignore**
```
# Dependencies
node_modules/
.pnp
.pnp.js

# Build
dist/
build/
*.local

# Environment
.env
.env.local
.env.production

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store
```

2. **frontend/tsconfig.node.json**
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

3. **frontend/.eslintrc.cjs**
```js
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}
```

4. **frontend/postcss.config.js**
```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

---

## Полный чеклист файлов

### ✅ Backend (обязательные)
- [x] main.py
- [x] requirements.txt
- [x] Dockerfile
- [x] docker-compose.yml
- [x] .env.example
- [x] app/__init__.py
- [x] app/api/__init__.py
- [x] app/api/dependencies.py
- [x] app/api/endpoints/__init__.py
- [x] app/api/endpoints/auth.py
- [x] app/api/endpoints/documents.py
- [x] app/api/endpoints/analysis.py
- [x] app/core/__init__.py
- [x] app/core/config.py
- [x] app/core/database.py
- [x] app/core/security.py
- [x] app/models/__init__.py
- [x] app/models/models.py
- [x] app/models/schemas.py
- [x] app/services/__init__.py
- [x] app/services/pgd_service.py
- [x] app/services/document_service.py
- [x] app/services/ai_service.py
- [x] app/utils/__init__.py

### ✅ Frontend (обязательные)
- [x] index.html
- [x] package.json
- [x] tsconfig.json
- [x] vite.config.ts
- [x] tailwind.config.js
- [x] Dockerfile
- [x] nginx.conf
- [x] .env.example
- [x] src/main.tsx
- [x] src/App.tsx
- [x] src/index.css
- [x] src/pages/LoginPage.tsx
- [x] src/pages/RegisterPage.tsx
- [x] src/pages/DashboardPage.tsx
- [x] src/pages/AnalysisPage.tsx
- [x] src/pages/HistoryPage.tsx
- [x] src/services/api.ts
- [x] src/stores/authStore.ts
- [x] src/types/api.ts

### ✅ Deployment
- [x] deployment/render.yaml
- [x] DEPLOYMENT.md
- [x] README.md

---

## Команды для запуска

### Локальная разработка

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Отредактируйте .env
npm run dev
```

### Docker (полный стек)

**Backend + PostgreSQL:**
```bash
cd backend
docker-compose up -d
```

**Frontend (production build):**
```bash
cd frontend
docker build -t career-frontend .
docker run -p 80:80 career-frontend
```

### Деплой на Render

**Автоматический (Blueprint):**
1. Загрузите на GitHub
2. Render Dashboard → New Blueprint
3. Выберите репозиторий
4. Добавьте `GOOGLE_API_KEY`
5. Deploy

**Ручной:**
См. [DEPLOYMENT.md](./DEPLOYMENT.md) для подробных инструкций

---

## Зависимости

### Backend (Python)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
google-generativeai==0.3.2
PyPDF2==3.0.1
python-docx==1.1.0
pdfplumber==0.10.3
pydantic==2.5.3
python-multipart==0.0.6
python-dotenv==1.0.0
```

### Frontend (NPM)
```
react@18.2.0
react-dom@18.2.0
react-router-dom@6.21.0
typescript@5.2.2
vite@5.0.8
tailwindcss@3.3.6
axios@1.6.2
zustand@4.4.7
recharts@2.10.3
react-dropzone@14.2.3
react-hot-toast@2.4.1
lucide-react@0.298.0
date-fns@3.0.6
```

---

## Размер проекта

**Строки кода:**
- Backend: ~2,500 строк Python
- Frontend: ~1,800 строк TypeScript/TSX
- Конфигурация: ~500 строк
- Документация: ~1,000 строк

**Файлов:**
- Backend: 25 файлов
- Frontend: 20 файлов
- Deployment: 3 файла
- Всего: ~50 файлов

---

**Версия:** 1.0
**Дата создания:** 2026-02-23
