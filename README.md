# 🛒 E-Commerce Base (FastAPI + Next.js 16)

A **production‑grade full‑stack boilerplate** using:

- **FastAPI (Python 3.12)** — Backend  
- **Next.js 16 (React + TypeScript)** — Frontend  
- **PostgreSQL + Alembic** — Database & Migrations  
- **Docker Compose (dev & prod profiles)** — Containerized environment  
- **JWT Auth with HttpOnly Cookies**, RBAC, file uploads, API routing, etc.

---

# 🚀 Features Overview

## 🧱 Backend (FastAPI)
- JWT Authentication (Access + Refresh)
- HttpOnly secure session cookies
- Role-Based Access Control (RBAC)
- Global exception handlers
- Structured success/error responses
- Logging with file rotation
- File uploads (local storage)
- PostgreSQL + SQLAlchemy + Alembic migrations
- Auto-seeding roles & admin user
- Development & Production Dockerfile

---

## 💻 Frontend (Next.js 16)
- Login using HttpOnly cookies (secure)
- Auto token refresh (Axios Interceptor)
- Global API wrapper
- React Query integration
- Tailwind CSS + Shadcn UI components
- Middleware-based route protection
- Fully typed API responses
- Development & Production Dockerfile

---

# 📦 Project Structure

```
ecommerce-base/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── storage/uploads/
│   │   └── main.py
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── requirements.txt
│   └── .env / .env.prod
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── .env / .env.prod
│
├── docker-compose.yml   ← dev/prod profiles
└── README.md
```

---

# ⚙️ Environment Setup

## 🌱 Backend Environment Files

### `backend/.env` (Development)
```
ENV=development
PROJECT_NAME="Ecommerce API (Dev)"
DATABASE_URL=postgresql://postgres:postgres@db:5432/ecommerce

ACCESS_SECRET=dev-access-secret
REFRESH_SECRET=dev-refresh-secret
ACCESS_EXPIRE_MINUTES=30
REFRESH_EXPIRE_DAYS=7

BACKEND_CORS_ORIGINS=http://localhost:3000
```

### `backend/.env.prod` (Production)
```
ENV=production
PROJECT_NAME="Ecommerce API (Prod)"
DATABASE_URL=postgresql://postgres:postgres@db:5432/ecommerce

ACCESS_SECRET=change-this-access-secret
REFRESH_SECRET=change-this-refresh-secret
ACCESS_EXPIRE_MINUTES=30
REFRESH_EXPIRE_DAYS=7

BACKEND_CORS_ORIGINS=https://yourdomain.com
```

---

## 🎨 Frontend Environment Files

### `frontend/.env` (Development)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### `frontend/.env.prod` (Production)
```
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
```

---

# 🐳 Docker Compose (Profiles)

This project uses **profiles**:

| Mode | Command | Services |
|------|---------|----------|
| Development | `npm run dev` | db, backend-dev, frontend-dev |
| Production | `npm run prod` | db, backend-prod, frontend-prod |

---

# ▶️ Start Development

Build dev mode:

```
npm run dev:build
```

```
npm run dev:start
```

Services:
- Backend → http://localhost:8000  
- Frontend → http://localhost:3000  
- PostgreSQL → port 5432  

Stop dev mode:

```
npm run dev:down
```

---

# 🚀 Start Production

Build prod mode:

```
npm run prod:build
```

```
npm run prod:start
```

Deploy-ready Docker services.

Stop production mode:

```
npm run prod:down
```

---

# 🧩 Backend Local Development (Optional)

```
cd backend
uvicorn app.main:app --reload
```

---

# 🌐 Frontend Development (Optional)

```
cd frontend
npm install
npm run dev
```

---

# 🔐 Authentication Flow

1. User logs in → receives **HttpOnly refresh token**
2. Access token (short-lived) returned in JSON
3. Axios interceptor auto-refreshes token when expired
4. Session stays secure using HttpOnly cookies
5. RBAC applied via API + Middleware

---

# 🧪 Default Seeded Users

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | admin123 | admin |
| user@example.com | user123 | user |

---

# 📄 Scripts

From root package.json:

```
npm run dev:build
npm run dev:start
npm run dev:down
npm run prod:build
npm run prod:start
npm run prod:down
npm run logs
npm run clean
```

---

# 📜 License
MIT License

---

# ⭐ Notes
This boilerplate is designed for building:
- E-Commerce platforms  
- Admin dashboards  
- Inventory systems  
- SaaS web apps  
- Company internal tools  

Feel free to customize and extend it!  
