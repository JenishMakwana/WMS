# CoreInventory 📦

A full-stack Inventory Management System built with **FastAPI**, **React (Vite/TS)**, and **PostgreSQL**.

---

## 🚀 Quick Start (Windows)

### Option 1: Using Docker (Recommended)
The easiest way to run the project is via Docker, which bundles all services (DB, Redis, API, Frontend).
1.  Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop) is running.
2.  Double-click **`run.bat`**.

### Option 2: Running Locally (No Docker)
To run the project directly on your machine:
1.  **Prerequisites:** 
    - [Python 3.12+](https://www.python.org/downloads/)
    - [Node.js / npm](https://nodejs.org/)
    - [PostgreSQL](https://www.postgresql.org/download/) & [Redis](https://redis.io/download/) installed and running locally.
2.  **Configuration:** Update `backend/.env` and change `db:5432` to `localhost:5432` and `redis:6379` to `localhost:6379`.
3.  Double-click **`run_local.bat`**.
    - This script sets up a Python virtual environment, installs all dependencies for both backend and frontend, and starts both servers.

---

## 🛠️ Manual Local Setup (Step-by-Step)

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Update with local DB credentials
alembic upgrade head
uvicorn app.main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 Accessing the App

| Method | Frontend URL | API Docs |
|----------|-----|-----|
| **Docker** | [http://localhost](http://localhost) | [http://localhost/api/docs](http://localhost/api/docs) |
| **Local** | [http://localhost:5173](http://localhost:5173) | [http://localhost:8000/api/docs](http://localhost:8000/api/docs) |

### Demo Credentials (after seeding)
-   **Manager:** `manager@coreinventory.com` / `Manager123!`
-   **Staff:** `staff@coreinventory.com` / `Staff123!`

---

## 📂 Project Structure

```bash
coreinventory/
├── backend/            # FastAPI + SQLAlchemy
├── frontend/           # React + Vite + Tailwind
├── run.bat             # Start via Docker
├── run_local.bat       # Start locally (Requires manual DB setup)
└── Makefile            # Docker shortcuts
```

---

## 📝 Common Commands

| Command | Description |
|---------|-------------|
| `make seed` | (Docker only) Seed demo data |
| `cd backend && venv\Scripts\activate && python -m app.seed` | (Local) Seed demo data |
| `make test` | Run backend tests |

---

## ⚖️ License
MIT License
