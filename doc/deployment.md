# Deployment Guide

## Overview

SCRIPT can be deployed in two ways:
1. **Docker Deployment** (Recommended for production and testing)
2. **Local Deployment** (Recommended for development)

---

## Docker Deployment

### Prerequisites

- Docker (20.10+)
- Docker Compose (1.29+)
- Git
- Domain name (for production)
- SSL certificate (for production, can use Let's Encrypt)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd script
```

### Step 2: Create Environment File

Create a `.env` file in the root directory:

```bash
# Environment mode
ITS_ENV="development-docker"  # or "production"

# Database credentials
DB_SERVICE_PW="your_strong_service_password"
DB_ROOT_PW="your_strong_root_password"

# JWT secrets (generate random strings)
JWT_SECRET="your_jwt_secret_key_min_32_chars"
USER_VERIFICATION_SECRET="your_verification_secret"
RESET_PWD_SECRET="your_reset_password_secret"

# Judge0 configuration
JUDGE0_MODE="local"  # or "remote"
# For remote Judge0:
# JUDGE0_URL="https://judge0-api.example.com"
# JUDGE0_TOKEN="your_judge0_api_token"

# Email configuration (production only)
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_SENDER="noreply@yourdomain.com"
EMAIL_USR="your_email@gmail.com"
EMAIL_PWD="your_email_app_password"
EMAIL_POSTFIX="@yourdomain.com"
```

**Generate Secrets:**
```bash
# Generate random secrets (Linux/macOS)
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Start Services

```bash
docker-compose up -d
```

This will start:
- MongoDB (port 27017)
- FastAPI Backend (port 8888)
- Angular Frontend (port 4200 dev, 8080 production)
- Judge0 Server (port 2358)
- Judge0 Workers

### Step 4: Verify Services

```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f

# Check specific service
docker-compose logs -f fastapi-backend
```

### Step 5: Access Application

- **Frontend**: http://localhost:8080 (production) or http://localhost:4200 (dev)
- **API Docs**: http://localhost:8888/api/docs
- **MongoDB**: localhost:27017

---

## Production Deployment

### Additional Steps for Production

#### 1. Configure Nginx for HTTPS

Edit `script/nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://angular-app:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://fastapi-backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 2. Update Docker Compose for Production

Ensure `ITS_ENV=production` in `.env`:

```bash
ITS_ENV="production"
```

#### 3. Configure Email Service

For production, email verification is enabled. Options:
- **Gmail**: Use app-specific password
- **SendGrid**: Use API key
- **Custom SMTP**: Configure your mail server

#### 4. Set Up SSL Certificate

**Using Let's Encrypt:**
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to nginx
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /path/to/script/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /path/to/script/ssl/key.pem
```

#### 5. Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to backend
sudo ufw deny 8888/tcp

# Enable firewall
sudo ufw enable
```

---

## Setting Up Admin User

### 1. Register User via UI

Navigate to registration page and create account.

### 2. Get Verification Token

**Development (console output):**
```bash
# Check backend logs
docker-compose logs fastapi-backend | grep "verification"
```

**Production (check email):**
User receives verification email.

### 3. Verify User

Visit: `http://yourdomain.com/verify?token=<verification_token>`

### 4. Grant Admin Role

```bash
# Access MongoDB
docker-compose exec mongodb mongosh -u useradmin -p

# Switch to its_db
use its_db

# Find user
db.User.find({username: "admin_username"})

# Update user with admin role
db.User.updateOne(
  {username: "admin_username"},
  {$set: {roles: ["admin", "tutor"]}}
)
```

**Roles:**
- `admin`: Full system access, can modify settings
- `tutor`: Can upload/modify courses
- (no role): Regular student

---

## Loading Courses

### Via UI (Recommended)

1. Log in as admin/tutor
2. Navigate to course selection page
3. Click "Upload Course" button
4. Select course folder containing:
   - `course.json`
   - Task folders with markdown files

### Via Command Line

```bash
# Copy course folder to backend container
docker cp ./courses/my_course fastapi-backend:/api/courses/

# Restart backend to load
docker-compose restart fastapi-backend
```

---

## Setting Up LLM Server

### Option 1: Local Ollama (Recommended)

#### 1. Set Up Ollama Container

```bash
cd llm-server
docker-compose up -d
```

#### 2. Pull Models

```bash
# Access ollama container
docker exec -it llm-server ollama pull qwen3-coder:30b

# Other recommended models
docker exec -it llm-server ollama pull codellama:13b
docker exec -it llm-server ollama pull deepseek-coder:6.7b
```

#### 3. Configure in SCRIPT

1. Log in as admin
2. Go to Settings
3. Set:
   - **API Type**: `ollama`
   - **API URL**: `http://llm-server:11434/`
   - **API Key**: (leave empty)

### Option 2: OpenAI API

1. Log in as admin
2. Go to Settings
3. Set:
   - **API Type**: `open-ai`
   - **API URL**: `https://api.openai.com/v1/`
   - **API Key**: `sk-...`

---

## Database Management

### Backup

```bash
# Run backup script
cd database_scripts
./backup_db.sh
```

Manual backup:
```bash
docker-compose exec mongodb mongodump \
  --username=useradmin \
  --password=<DB_ROOT_PW> \
  --authenticationDatabase=admin \
  --db=its_db \
  --out=/data/backup
```

### Restore

```bash
# Run restore script
cd database_scripts
./restore_collections.sh
```

Manual restore:
```bash
docker-compose exec mongodb mongorestore \
  --username=useradmin \
  --password=<DB_ROOT_PW> \
  --authenticationDatabase=admin \
  --db=its_db \
  /data/backup/its_db
```

### Database Access

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh -u useradmin -p

# Use its_db
use its_db

# Query users
db.User.find().pretty()

# Query courses
db.Course.find().pretty()
```

---

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi-backend
docker-compose logs -f angular-app
docker-compose logs -f mongodb

# Last 100 lines
docker-compose logs --tail=100 fastapi-backend
```

### Log Rotation

Logs are automatically rotated (max 100MB per file) via Docker logging configuration.

### Monitor Resource Usage

```bash
# Container stats
docker stats

# Specific container
docker stats fastapi-backend
```

---

## Scaling & Performance

### Horizontal Scaling

The FastAPI backend is stateless and can be scaled:

```yaml
# docker-compose.yml
services:
  fastapi-backend:
    deploy:
      replicas: 3
```

Add load balancer (e.g., Nginx upstream):

```nginx
upstream backend {
    server fastapi-backend:8000;
    server fastapi-backend-2:8000;
    server fastapi-backend-3:8000;
}
```

### Database Optimization

1. **Indexes**: Ensure proper indexes (see database-schema.md)
2. **Connection Pooling**: Configured via Motor
3. **Replica Set**: For high availability

```yaml
# docker-compose.yml for replica set
mongodb-primary:
  image: mongo:5.0
  command: mongod --replSet rs0

mongodb-secondary:
  image: mongo:5.0
  command: mongod --replSet rs0
```

---

## Security Checklist

- [ ] Strong passwords in `.env`
- [ ] SSL/TLS enabled
- [ ] Firewall configured
- [ ] Database access restricted
- [ ] Admin users properly secured
- [ ] Regular backups scheduled
- [ ] Logs monitored
- [ ] Dependencies updated
- [ ] API rate limiting (recommended)
- [ ] CORS properly configured

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Check credentials in .env
cat .env | grep DB_

# Test connection
docker-compose exec fastapi-backend python -c "
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient('mongodb://backend_service_user:PASSWORD@mongodb:27017')
print(client.list_database_names())
"
```

### Frontend Can't Reach Backend

- Check nginx.conf proxy settings
- Verify backend is running: `docker-compose logs fastapi-backend`
- Test API directly: `curl http://localhost:8888/api/docs`

### Judge0 Errors

```bash
# Check Judge0 services
docker-compose logs j0-server
docker-compose logs j0-workers

# Restart Judge0
docker-compose restart j0-server j0-workers
```

### LLM Feedback Not Working

- Verify LLM server is accessible
- Check admin settings configuration
- Test API manually:
```bash
curl http://llm-server:11434/api/generate \
  -d '{"model": "qwen3-coder:30b", "prompt": "Hello"}'
```

---

## Updating SCRIPT

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d

# Check for database migrations
docker-compose exec fastapi-backend python -m beanie migrate
```

---

## Uninstalling

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker rmi $(docker images | grep script)
```

---

## Support

For issues:
1. Check logs
2. Review documentation
3. Contact KML group at Bielefeld University
4. Open GitHub issue (if repository is public)
