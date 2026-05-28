# Development Setup Guide

## Overview

This guide helps you set up a local development environment for SCRIPT. Local development provides faster iteration, better debugging, and easier testing.

---

## Prerequisites

### Required Software

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **Angular CLI** (`npm install -g @angular/cli`)
- **MongoDB 5.0+**
- **Docker & Docker Compose** (for Judge0)
- **Git**

### Recommended Tools

- **VS Code** with extensions:
  - Python
  - Angular Language Service
  - Docker
  - MongoDB for VS Code
- **Postman** or **Insomnia** (API testing)
- **MongoDB Compass** (database GUI)
- **Conda** or **venv** (Python virtual environment)

---

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd script
```

---

## Step 2: Set Up Environment Variables

Create `.env` file in root directory:

```bash
# Environment
ITS_ENV="development"

# Database
DB_SERVICE_PW="dev_password"
DB_ROOT_PW="dev_root_password"

# JWT Secrets
JWT_SECRET="dev_jwt_secret_min_32_characters_long"
USER_VERIFICATION_SECRET="dev_verification_secret"
RESET_PWD_SECRET="dev_reset_password_secret"

# Judge0 (local)
JUDGE0_MODE="local"

# Email (disabled in development)
# EMAIL_HOST=""
# EMAIL_PORT=""
# EMAIL_SENDER=""
# EMAIL_USR=""
# EMAIL_PWD=""
# EMAIL_POSTFIX=""
```

---

## Step 3: Set Up MongoDB

### Install MongoDB

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community@5.0
brew services start mongodb-community@5.0
```

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
Download and install from https://www.mongodb.com/try/download/community

### Create Database User

```bash
# Connect to MongoDB
mongosh

# Create admin user
use admin
db.createUser({
  user: "useradmin",
  pwd: "dev_root_password",
  roles: ["root"]
})

# Create service user
use admin
db.createUser({
  user: "backend_service_user",
  pwd: "dev_password",
  roles: [
    { role: "readWrite", db: "its_db" }
  ]
})

# Exit
exit
```

### Verify Connection

```bash
mongosh -u backend_service_user -p dev_password --authenticationDatabase admin
```

---

## Step 4: Set Up Judge0

Judge0 handles code execution. Use Docker for easy setup:

```bash
cd judge0
docker-compose up -d
cd ..
```

Verify Judge0 is running:
```bash
curl http://localhost:2358/about
```

---

## Step 5: Set Up Backend (FastAPI)

### Create Virtual Environment

**Using Conda:**
```bash
cd api
conda create -n script-dev python=3.10
conda activate script-dev
```

**Using venv:**
```bash
cd api
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import fastapi; import beanie; print('Dependencies installed successfully')"
```

### Run Backend

```bash
python main.py
```

Backend should start on http://localhost:8000

**API Documentation**: http://localhost:8000/api/docs

---

## Step 6: Set Up Frontend (Angular)

### Install Dependencies

```bash
cd frontend/its_ui
npm install
```

### Run Development Server

```bash
ng serve
```

Frontend should start on http://localhost:4200

**Or use VS Code tasks:**
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "ng serve"

---

## Step 7: Set Up LLM Server (Optional)

For AI feedback functionality:

### Option 1: Local Ollama

```bash
cd llm-server
docker-compose up -d

# Pull model
docker exec -it llm-server ollama pull qwen3-coder:30b
```

### Option 2: Use OpenAI

Configure in admin settings after setup.

---

## Development Workflow

### Starting Development Session

```bash
# Terminal 1: Backend
cd api
conda activate script-dev  # or source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend/its_ui
ng serve

# Terminal 3: Judge0 (if not running)
cd judge0
docker-compose up

# Terminal 4: LLM Server (optional)
cd llm-server
docker-compose up
```

### Using start_app.py Script

Alternatively, use the provided startup script:

```bash
python start_app.py
```

This script starts all services automatically.

---

## Creating Test Data

### 1. Register Admin User

Navigate to http://localhost:4200/register

- Username: `admin`
- Email: `admin@test.com`
- Password: `admin123`
- Check both consent boxes

### 2. Get Verification Token

Check backend console output for verification token:
```
Verification token: abc123...
```

### 3. Verify User

Navigate to:
```
http://localhost:4200/verify?token=abc123...
```

### 4. Grant Admin Role

```bash
mongosh -u backend_service_user -p dev_password --authenticationDatabase admin

use its_db
db.User.updateOne(
  {username: "admin"},
  {$set: {roles: ["admin", "tutor"]}}
)
```

### 5. Load Test Course

```bash
# Copy test course
cp -r courses/test_course api/courses/

# Or use UI after logging in as admin
```

---

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/api/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true
  }
}
```

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "cwd": "${workspaceFolder}/api",
      "env": {
        "ITS_ENV": "development"
      }
    },
    {
      "name": "Angular: serve",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/frontend/its_ui/node_modules/@angular/cli/bin/ng",
      "args": ["serve"],
      "cwd": "${workspaceFolder}/frontend/its_ui"
    }
  ]
}
```

---

## Testing

### Backend Tests

```bash
cd api
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_handle_submissions.py
```

### Frontend Tests

```bash
cd frontend/its_ui

# Unit tests
ng test

# E2E tests
ng e2e
```

---

## Database Management

### View Database

**MongoDB Compass:**
Connection string: `mongodb://backend_service_user:dev_password@localhost:27017/its_db?authSource=admin`

**Command Line:**
```bash
mongosh -u backend_service_user -p dev_password --authenticationDatabase admin its_db

# Useful queries
db.User.find().pretty()
db.Course.find().pretty()
db.Task.find({}, {unique_name: 1, display_name: 1}).pretty()
db.Submission.countDocuments()
```

### Reset Database

```bash
mongosh -u useradmin -p dev_root_password --authenticationDatabase admin

use its_db
db.dropDatabase()
```

---

## Debugging

### Backend Debugging

**VS Code:**
1. Set breakpoints in Python files
2. Press F5 or use "Run and Debug" panel
3. Select "Python: FastAPI" configuration

**Print Debugging:**
```python
print(f"Debug: {variable}")  # Simple
import pprint; pprint.pprint(complex_object)  # Complex objects
```

**Logging:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Info message")
logger.error("Error message")
```

### Frontend Debugging

**Browser DevTools:**
- Press F12
- Use Console for errors
- Network tab for API calls
- Sources tab for breakpoints

**Angular DevTools:**
Install Chrome extension: "Angular DevTools"

---

## Common Issues

### MongoDB Connection Failed

**Error:** `pymongo.errors.ServerSelectionTimeoutError`

**Solution:**
```bash
# Check MongoDB is running
sudo systemctl status mongod  # Linux
brew services list  # macOS

# Start MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Judge0 Not Responding

```bash
# Check Judge0 containers
docker ps | grep j0

# Restart Judge0
cd judge0
docker-compose restart

# Check logs
docker-compose logs j0-server
```

### Frontend Build Errors

```bash
# Clear cache
cd frontend/its_ui
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Python Import Errors

```bash
# Verify virtual environment
which python  # Should point to venv/conda

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Hot Reloading

### Backend

FastAPI auto-reloads on file changes (via `--reload` flag).

**Manual restart:**
```bash
# Stop with Ctrl+C
# Restart
python main.py
```

### Frontend

Angular auto-reloads on file changes.

**Force rebuild:**
```bash
ng serve --poll=2000  # Poll every 2 seconds
```

---

## Code Style

### Python

Use Black formatter:
```bash
cd api
black .
```

Use isort for imports:
```bash
isort .
```

### TypeScript/Angular

Use Prettier:
```bash
cd frontend/its_ui
npm run format
```

---

## Git Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
git add .
git commit -m "Add feature X"

# Push to remote
git push origin feature/my-feature

# Create pull request
```

### Commit Messages

Follow conventional commits:
```
feat: Add new feature
fix: Fix bug in submissions
docs: Update API documentation
refactor: Refactor task selection
test: Add tests for feedback system
```

---

## Performance Profiling

### Backend

```bash
# Install profiler
pip install py-spy

# Profile running application
py-spy top --pid <python_pid>

# Generate flamegraph
py-spy record -o profile.svg -- python main.py
```

### Frontend

Use Chrome DevTools:
1. Open DevTools (F12)
2. Performance tab
3. Click Record
4. Interact with app
5. Stop recording
6. Analyze flame chart

---

## Useful Commands

```bash
# Backend
cd api && python main.py
cd api && pytest
cd api && black . && isort .

# Frontend
cd frontend/its_ui && ng serve
cd frontend/its_ui && ng test
cd frontend/its_ui && ng build --prod

# Database
mongosh -u backend_service_user -p dev_password --authenticationDatabase admin its_db
mongodump --db=its_db --out=backup
mongorestore --db=its_db backup/its_db

# Docker
docker-compose up -d judge0
docker-compose logs -f
docker-compose down
```

---

## Next Steps

1. Read [Architecture Documentation](architecture.md)
2. Review [API Reference](api-reference.md)
3. Study [Course Structure](course-structure.md)
4. Explore [Models Documentation](models.md)
5. Start contributing!

---

## Getting Help

- Check documentation in `doc/` folder
- Review code comments
- Search existing issues
- Ask in development chat
- Contact maintainers
