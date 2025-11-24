# 🛒 E-Commerce Base

> A **production-grade full-stack boilerplate** built with  
> **FastAPI (Python)** for the backend and **Next.js 16 (React + TypeScript)** for the frontend.  
> Includes secure authentication with HttpOnly cookies, JWT access + refresh tokens, RBAC, file uploads, PostgreSQL, Alembic migrations, and a complete Docker Compose environment.

---

## ✨ Features

### 🧱 Backend (FastAPI)
- 🔐 **Authentication**
  - JWT Access Token (short-lived)
  - Refresh Token (HttpOnly Cookie)
  - Secure cookie-based session
- 🛡 **RBAC (Role-Based Access Control)**
  - Middleware-level & API-level authorization
  - Admin-only endpoints
- 📦 **Models Included**
  - User  
  - Role  
  - Product (with images, CRUD, search)
- 📂 **File Upload System**
  - Secure image uploads
  - Physical storage + public serving
- 🧱 **Database**
  - PostgreSQL  
  - Alembic migrations  
  - Auto-seeding for Roles & Admin/User accounts
- 🧰 **Utilities**
  - Structured error formatting (`SuccessResponse`, `ErrorResponse`)
  - Logging middleware with rotation
  - CORS support
  - Global exception handlers

---

### 💻 Frontend (Next.js 16 + React)
- 🔐 **Authentication System**
  - Login with HttpOnly cookie session
  - Auto-refresh token via API interceptor
  - React Query integration
  - `useLogin`, `useRegister`, `useMe`, `logout()`
- 🛡 **Route Protection**
  - Next.js Middleware for RBAC
  - Automatic login redirect
  - Safe `redirect` handling
- 🎨 **UI Layer**
  - Tailwind CSS
  - Shadcn UI Components
  - Minimalistic & clean defaults
- 🛠 **Utilities**
  - Axios API wrapper with auto-refresh logic
  - Error toast handling (`sonner`)
  - Typed API responses & schemas

---

## 🏗 Project Structure (Simplified)

```
ecommerce-base/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── storage/uploads/
│   │   └── main.py
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/username/ecommerce-base.git
cd ecommerce-base
```

---

## 2️⃣ Environment Variables

### **Backend (.env)**
```
APP_ENV=development
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/postgres

ACCESS_SECRET=your_access_secret
REFRESH_SECRET=your_refresh_secret
ACCESS_EXPIRE_MINUTES=30
REFRESH_EXPIRE_DAYS=7

BACKEND_CORS_ORIGINS=http://localhost:3000
PROJECT_NAME=E-Commerce Base
```

### **Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 3️⃣ Install Dependencies

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

Or use the helper script:
```bash
npm run setup
```

---

## 4️⃣ Start Development (Docker)

```bash
docker compose up --build
```

Services:
- Backend → http://localhost:8000  
- Frontend → http://localhost:3000  
- PostgreSQL → port 5432  

---

## 5️⃣ Automatic Seeds

Upon first backend startup, the system automatically seeds:

### Roles:
- admin
- user

### Default Users:
| Email | Password | Role |
|-------|----------|------|
| admin@example.com | admin123 | admin |
| user@example.com  | user123  | user  |

---

## 🧪 Testing Authentication

### Login
```http
POST /auth/login
```

### Auto-refresh  
Browser sends the HttpOnly `refresh_token` automatically.

### Protected Route  
Admin-only route:  
`/products` (create/update/delete)

---

## 📦 Production Build

### Docker (Recommended)
```bash
npm run build
npm run start
```

### Backend (Optional)
```bash
docker compose -f docker-compose.prod.yml up --build
```

### Frontend (Optional)
```bash
npm run build
npm run start
```

---

## 📄 License
MIT — open for personal or commercial use.

---

## ❤️ Contributing
Feel free to open PRs and issues to improve this starter template.

---

## ⚡ Ready to Build Real E-Commerce?
This boilerplate accelerates development for:

- SaaS Dashboard  
- Admin Panel  
- B2B/B2C Web Store  
- Company Internal Tools  
- Inventory Management Systems  
