# Caterpillar Smart Rental Tracking System

This repository contains the complete source code for the Caterpillar Smart Rental Tracking System, featuring a FastAPI backend, a React frontend, and a real-time RabbitMQ notification system.

## Running the Application Locally

To get the full system up and running, you will need to start three separate services. Open three different terminal windows in your code editor to run these concurrently.

### 1. Start RabbitMQ (Message Broker)
The backend uses RabbitMQ to process real-time notifications asynchronously (like overdue alerts and machine transfers). You can spin up a local instance easily using Docker.

Run this from any terminal:
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
*(The web dashboard will be available at `http://localhost:15672` using `guest`/`guest` as credentials).*

### 2. Start the Backend (FastAPI)
The backend requires Python and a PostgreSQL database connection string in its `.env` file. 

Open a terminal, navigate to the `backend/` directory, and start Uvicorn:
```bash
cd backend
# Make sure your virtual environment is activated:
# Windows: .\venv\Scripts\Activate.ps1
# Mac/Linux: source venv/bin/activate

uvicorn app.main:app --reload
```
*(The API will be available at `http://127.0.0.1:8000` and Swagger docs at `/docs`).*

### 3. Start the Frontend (React / Vite)
The frontend requires Node.js. 

Open a terminal, navigate to the `frontend/` directory, and start the Vite dev server:
```bash
cd frontend
# If you haven't installed packages yet, run: npm install

npm run dev
```
*(The UI will be available at `http://localhost:5173`).*

---

## Role-Based Access
You can log in to the application using any of the seeded test accounts to explore the different dashboards:
- **Cat Admin:** `admin@cat.com` / `password123`
- **Dealer:** `dealer1@cat.com` / `password123`
- **Customer:** `john.doe@email.com` / `password123`
- **Fleet Manager:** `fleet1@cat.com` / `password123`
