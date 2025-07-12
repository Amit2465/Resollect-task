# Resollect-task

## Project Overview

Resollect-task is a FastAPI-based web application using PostgreSQL and Redis, containerized with Docker Compose. It features robust authentication, task management, and is ready for production deployment on the cloud.

---

## Live Deployment

**Production URL:**

[http://15.207.114.128:8000/docs#/](http://15.207.114.128:8000/docs#/)

This link opens the Swagger UI, where all API endpoints can be tested interactively in the browser.

---

## API Documentation (Swagger UI)

The project uses FastAPI's built-in Swagger UI for interactive API documentation and testing.

- Local access: [http://localhost:8000/docs](http://localhost:8000/docs)
- Production access: [http://15.207.114.128:8000/docs#/](http://15.207.114.128:8000/docs#/)

All available endpoints and their schemas are visible here. Requests and responses can be tried out directly in the browser for quick manual testing and exploration.

---

## API Endpoints

### Authentication

```http
POST /v1/auth/register
```
Register a new user with email and password. Returns user details on success.

```http
POST /v1/auth/login
```
Authenticate a user and return a JWT access token for subsequent requests.

### Tasks (All endpoints require authentication)

```http
POST /v1/tasks/
```
Create a new task for the current user. Requires title, description, and deadline.

```http
GET /v1/tasks/
```
Retrieve all tasks for the current user. Returns a list of tasks with their statuses.

```http
GET /v1/tasks/{task_id}
```
Retrieve a single task by its ID for the current user.

```http
PUT /v1/tasks/{task_id}
```
Update the details of a task (title, description, deadline, etc.).

```http
PATCH /v1/tasks/{task_id}/complete
```
Mark a task as completed.

```http
DELETE /v1/tasks/{task_id}
```
Delete a task owned by the current user.

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Amit2465/Resollect-task.git
cd Resollect-task
```

### 2. Install Python Dependencies
Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root for local development:
```env
SECRET_KEY=some_secret_key # This is for password Hashing 
REDIS_URL=redis://localhost:6379
```
Database settings are managed by Docker Compose and do not need to be set in `.env` for local Docker runs.

### 4. Start Services with Docker Compose
```bash
docker-compose up -d --build
```
This command starts the FastAPI app, PostgreSQL, and Redis containers.

### 5. Access the Application
- The app runs at [http://localhost:8000](http://localhost:8000).
- The API docs and testing UI are at [http://localhost:8000/docs](http://localhost:8000/docs).
- The production deployment is at [http://15.207.114.128:8000/docs#/](http://15.207.114.128:8000/docs#/).

---

## Deployment (CI/CD)

Deployment is automated via GitHub Actions. On every push to `main`:
- The code is copied to the EC2 instance.
- A new `.env` is created with secrets (except DB settings, which are in `docker-compose.yml`).
- Old containers are stopped, new ones are built and started.
- Postgres data is preserved between deployments.

---

## Useful Commands

- Stop all containers:
  ```bash
  docker-compose down
  ```
- Rebuild and restart:
  ```bash
  docker-compose up -d --build
  ```
- View logs:
  ```bash
  docker-compose logs -f
  ```

---

## Troubleshooting
- Docker and Docker Compose must be installed.
- If DB credentials change, update both `docker-compose.yml` and the GitHub secrets.
- For local development, ensure ports 8000 (FastAPI), 5432 (Postgres), and 6379 (Redis) are available.

