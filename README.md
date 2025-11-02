# 🛒 E-Commerce Base

> Full-stack boilerplate menggunakan **FastAPI (Python)** untuk backend dan **Next.js 16 (React + TypeScript)** untuk frontend.  
> Sudah dilengkapi autentikasi JWT + refresh token, role based access control (RBAC), sistem upload, migrasi database (Alembic), serta Docker Compose setup siap pakai.

---

## ✨ Fitur Utama

### 🧱 Backend (FastAPI)
- ✅ Auth JWT + Refresh Token + Cookie Secure  
- ✅ Role Based Access Control (Admin / Seller / User)  
- ✅ Model User / Role / Product  
- ✅ Alembic Migration & Auto Init Roles  
- ✅ Standard Response Format (`SuccessResponse` / `ErrorResponse`)  
- ✅ Rotating Logs + CORS + Structured Exception Handler  
- ✅ Dockerized PostgreSQL + FastAPI App  

### 💻 Frontend (Next.js 16)
- ✅ React Query + Axios API Wrapper  
- ✅ Auth Context & Token Storage (LocalStorage + Memory)  
- ✅ Middleware RBAC / Login Redirect Control  
- ✅ Tailwind CSS + Shadcn UI Components  
- ✅ SSR-safe Auth Logic & Auto-Redirect  
- ✅ Hooks (`useLogin`, `useRegister`, `useMe`)  
- ✅ Product List / Detail / CRUD Sample Pages  

---

## 🚀 Getting Started

### 1️⃣ Clone Repository
```bash
git clone https://github.com/username/ecommerce-base.git
cd ecommerce-base
```

### 2️⃣ Environment Variables
```bash
APP_ENV=production
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/postgres

BACKEND_PORT=8000
FRONTEND_PORT=3000
CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3️⃣ Setup Dependencies
```bash
npm run setup
```

### 4️⃣ Start Development
```bash
npm run start
```
