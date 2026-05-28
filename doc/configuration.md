# Configuration Reference

## Overview

SCRIPT configuration is managed through environment variables (`.env` file) and runtime settings. This document describes all available configuration options.

---

## Environment Variables

### Required Variables

#### ITS_ENV

**Type**: `string`  
**Values**: `development`, `development-docker`, `production`  
**Description**: Determines the runtime environment

**Example:**
```bash
ITS_ENV="production"
```

**Effects:**
- `development`: Local development, local MongoDB, no email
- `development-docker`: Docker-based, Judge0 in Docker
- `production`: All services containerized, email enabled

---

#### DB_SERVICE_PW

**Type**: `string`  
**Required**: Yes  
**Description**: Password for backend MongoDB service user

**Example:**
```bash
DB_SERVICE_PW="your_strong_password_here"
```

**Security**: Use strong passwords (20+ characters, mixed case, numbers, symbols)

---

#### DB_ROOT_PW

**Type**: `string`  
**Required**: Yes  
**Description**: Password for MongoDB root user (useradmin)

**Example:**
```bash
DB_ROOT_PW="your_root_password_here"
```

**Security**: Even stronger than service password, rarely used

---

#### JWT_SECRET

**Type**: `string`  
**Required**: Yes  
**Minimum Length**: 32 characters  
**Description**: Secret key for JWT token signing

**Example:**
```bash
JWT_SECRET="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
```

**Generation:**
```bash
openssl rand -hex 32
```

**Security**: Never commit to version control, rotate periodically

---

#### USER_VERIFICATION_SECRET

**Type**: `string`  
**Required**: Yes  
**Description**: Secret for email verification tokens

**Example:**
```bash
USER_VERIFICATION_SECRET="verification_secret_32_chars_min"
```

**Generation:** Same as JWT_SECRET

---

#### RESET_PWD_SECRET

**Type**: `string`  
**Required**: Yes  
**Description**: Secret for password reset tokens

**Example:**
```bash
RESET_PWD_SECRET="reset_secret_32_chars_minimum_length"
```

**Generation:** Same as JWT_SECRET

---

#### JUDGE0_MODE

**Type**: `string`  
**Values**: `local`, `remote`  
**Required**: Yes  
**Description**: Judge0 code execution mode

**Example:**
```bash
JUDGE0_MODE="local"
```

**Options:**
- `local`: Use self-hosted Judge0 (Docker)
- `remote`: Use external Judge0 API

---

### Judge0 Configuration (Remote Mode)

#### JUDGE0_URL

**Type**: `string`  
**Required**: Only if `JUDGE0_MODE=remote`  
**Description**: URL of Judge0 API

**Example:**
```bash
JUDGE0_URL="https://judge0-ce.p.rapidapi.com"
```

---

#### JUDGE0_TOKEN

**Type**: `string`  
**Required**: Only if `JUDGE0_MODE=remote`  
**Description**: API token for Judge0 service

**Example:**
```bash
JUDGE0_TOKEN="your_judge0_api_token"
```

---

### Email Configuration (Production Only)

#### EMAIL_HOST

**Type**: `string`  
**Required**: Production only  
**Description**: SMTP server hostname

**Example:**
```bash
EMAIL_HOST="smtp.gmail.com"
```

**Common Values:**
- Gmail: `smtp.gmail.com`
- SendGrid: `smtp.sendgrid.net`
- Mailgun: `smtp.mailgun.org`

---

#### EMAIL_PORT

**Type**: `integer`  
**Required**: Production only  
**Default**: `587`  
**Description**: SMTP server port

**Example:**
```bash
EMAIL_PORT="587"
```

**Common Values:**
- TLS: `587`
- SSL: `465`
- Unencrypted: `25` (not recommended)

---

#### EMAIL_SENDER

**Type**: `string`  
**Required**: Production only  
**Description**: Email address shown as sender

**Example:**
```bash
EMAIL_SENDER="noreply@yourdomain.com"
```

---

#### EMAIL_USR

**Type**: `string`  
**Required**: Production only  
**Description**: SMTP authentication username

**Example:**
```bash
EMAIL_USR="your_email@gmail.com"
```

---

#### EMAIL_PWD

**Type**: `string`  
**Required**: Production only  
**Description**: SMTP authentication password

**Example:**
```bash
EMAIL_PWD="your_app_specific_password"
```

**For Gmail**: Use app-specific password, not account password

---

#### EMAIL_POSTFIX

**Type**: `string`  
**Required**: Production only  
**Description**: Email domain for verification links

**Example:**
```bash
EMAIL_POSTFIX="@yourdomain.com"
```

---

## Application Settings (Runtime)

These settings are configured via the admin UI or directly in the database (`app_settings` collection).

### LLM API Configuration

#### api_type

**Type**: `string`  
**Values**: `ollama`, `open-ai`  
**Description**: LLM API provider

**Default**: `ollama`

**Example (Ollama):**
```json
{
  "api_type": "ollama",
  "api_url": "http://llm-server:11434/",
  "api_key": null
}
```

**Example (OpenAI):**
```json
{
  "api_type": "open-ai",
  "api_url": "https://api.openai.com/v1/",
  "api_key": "sk-..."
}
```

---

#### api_url

**Type**: `string`  
**Description**: Base URL for LLM API

**Examples:**
- Ollama local: `http://localhost:11434/`
- Ollama Docker: `http://llm-server:11434/`
- OpenAI: `https://api.openai.com/v1/`

---

#### api_key

**Type**: `string | null`  
**Description**: API key for LLM service

**Usage:**
- Ollama (local): `null`
- OpenAI: `"sk-..."`
- Other providers: API key as string

---

### Email Settings (Runtime)

#### email_enabled

**Type**: `boolean`  
**Description**: Enable/disable email sending

**Values:**
- `true`: Send verification and reset emails
- `false`: Print tokens to console (development)

**Auto-configured based on `ITS_ENV`:**
- `development`: `false`
- `production`: `true`

---

## Course Settings

Configured per-course in `course.json` or via admin UI.

### pedagogical_model

**Type**: `string`  
**Description**: Pedagogical model for the course

**Available Models:**
- `skipping_pfa` (default)
- `state-space`
- `simple-state-space`
- `prototype`
- `prototype_textual_feedback`
- `prototype_code_feedback`
- `group_A`, `group_B`, `group_C`, `group_D`

**Example:**
```json
{
  "pedagogical_model": "skipping_pfa"
}
```

See [Models Documentation](models.md) for details.

---

### language_generation_model

**Type**: `string`  
**Description**: LLM model for feedback generation

**Values:**
- `"default"`: Use system default
- `"qwen3-coder:30b"`: Qwen 3 Coder 30B
- `"codellama:13b"`: CodeLlama 13B
- `"gpt-4"`: OpenAI GPT-4
- `"gpt-3.5-turbo"`: OpenAI GPT-3.5 Turbo

**Example:**
```json
{
  "language_generation_model": "qwen3-coder:30b"
}
```

---

### feedback_init_time

**Type**: `integer`  
**Unit**: Seconds  
**Description**: Delay before feedback button appears

**Default**: `60`

**Purpose**: Prevent immediate feedback requests, encourage self-debugging

**Example:**
```json
{
  "feedback_init_time": 60
}
```

---

### feedback_cooldown

**Type**: `integer`  
**Unit**: Seconds  
**Description**: Minimum time between feedback requests

**Default**: `30`

**Purpose**: Prevent spam, encourage reflection

**Example:**
```json
{
  "feedback_cooldown": 30
}
```

---

## Database Configuration

### Connection String Format

```
mongodb://<user>:<password>@<host>:<port>/?authSource=admin
```

### Development (Local)

```python
DATABASE_URL = f"mongodb://backend_service_user:{DB_SERVICE_PW}@localhost:27017/?authSource=admin"
```

### Production (Docker)

```python
DATABASE_URL = f"mongodb://backend_service_user:{DB_SERVICE_PW}@mongodb:27017/?authSource=admin"
```

### Configuration in Code

**File**: `api/config.py`

```python
class Config:
    def __init__(self):
        self.env = os.environ.get("ITS_ENV", "development")
        
        if self.env == "development":
            self.database_host = "localhost"
            self.database_port = 27017
        elif self.env in ["development-docker", "production"]:
            self.database_host = "mongodb"
            self.database_port = 27017
```

---

## Judge0 Configuration

### Local Judge0 Config

**File**: `judge0/judge0.conf`

```ini
REDIS_HOST=localhost
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=your_password

# Resource limits
MAX_CPU_TIME=5
MAX_MEMORY=256000
MAX_PROCESSES=60
MAX_FILE_SIZE=1024
```

### Docker Compose Config

**File**: `judge0/docker-compose.yml`

```yaml
services:
  judge0:
    image: judge0/judge0:1.13.0-extra
    volumes:
      - ./judge0.conf:/judge0.conf:ro
    ports:
      - "2358:2358"
    privileged: true
```

---

## Nginx Configuration

**File**: `script/nginx.conf`

```nginx
upstream backend {
    server fastapi-backend:8000;
}

upstream frontend {
    server angular-app:80;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://frontend/;
    }
}
```

---

## Docker Compose Configuration

**File**: `docker-compose.yml`

### Service Configuration

```yaml
services:
  fastapi-backend:
    environment:
      ITS_ENV: ${ITS_ENV}
      DB_SERVICE_PW: ${DB_SERVICE_PW}
      JWT_SECRET: ${JWT_SECRET}
      # ... other env vars
    ports:
      - "8888:8000"
    
  mongodb:
    environment:
      MONGO_INITDB_ROOT_USERNAME: useradmin
      MONGO_INITDB_ROOT_PASSWORD: ${DB_ROOT_PW}
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
```

---

## Frontend Configuration

### Environment Files

**Development**: `frontend/its_ui/src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8888/api'
};
```

**Production**: `frontend/its_ui/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: '/api'  // Relative URL (via Nginx)
};
```

### Angular Configuration

**File**: `frontend/its_ui/angular.json`

```json
{
  "projects": {
    "its-ui": {
      "architect": {
        "build": {
          "configurations": {
            "production": {
              "fileReplacements": [
                {
                  "replace": "src/environments/environment.ts",
                  "with": "src/environments/environment.prod.ts"
                }
              ],
              "optimization": true,
              "outputHashing": "all",
              "sourceMap": false,
              "extractCss": true,
              "namedChunks": false,
              "aot": true,
              "buildOptimizer": true
            }
          }
        }
      }
    }
  }
}
```

---

## Security Best Practices

### Secrets Management

1. **Never commit `.env` to version control**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use strong, random secrets**
   ```bash
   # Generate secrets
   openssl rand -hex 32
   ```

3. **Rotate secrets regularly**
   - JWT secrets: Every 6 months
   - Database passwords: Annually
   - API keys: When compromised

4. **Use environment-specific secrets**
   - Development: Simple passwords
   - Production: Complex passwords

---

### Environment Separation

**Development:**
```bash
ITS_ENV="development"
DB_SERVICE_PW="dev_password"
JWT_SECRET="dev_secret_32_chars_min"
EMAIL_ENABLED="false"
```

**Production:**
```bash
ITS_ENV="production"
DB_SERVICE_PW="prod_strong_password_here"
JWT_SECRET="prod_random_secret_32_chars"
EMAIL_ENABLED="true"
```

---

## Configuration Checklist

### Development Setup

- [ ] `.env` file created
- [ ] `ITS_ENV=development`
- [ ] Database passwords set
- [ ] JWT secrets set (can be simple)
- [ ] Judge0 mode configured
- [ ] MongoDB running locally
- [ ] Judge0 running (Docker)

### Production Deployment

- [ ] `.env` file created with strong secrets
- [ ] `ITS_ENV=production`
- [ ] Strong database passwords (20+ chars)
- [ ] Random JWT secrets (32+ chars)
- [ ] Email configuration complete
- [ ] SSL certificates configured
- [ ] Firewall rules set
- [ ] Backup strategy in place
- [ ] Monitoring configured

---

## Troubleshooting

### "Environment variable not set"

**Error:**
```
KeyError: 'DB_SERVICE_PW'
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check variable is set
cat .env | grep DB_SERVICE_PW

# Restart services
docker-compose down
docker-compose up -d
```

---

### "Invalid JWT secret"

**Error:**
```
JWT secret must be at least 32 characters
```

**Solution:**
```bash
# Generate new secret
openssl rand -hex 32

# Update .env
JWT_SECRET="<generated_secret>"
```

---

### "Email sending failed"

**Check:**
1. Email enabled: `EMAIL_ENABLED=true`
2. Credentials correct
3. SMTP port accessible
4. App-specific password (for Gmail)

---

### "MongoDB authentication failed"

**Check:**
1. Password matches `.env` and MongoDB user
2. User has correct permissions
3. MongoDB is running

**Fix:**
```bash
# Connect as root
mongosh -u useradmin -p

# Recreate service user
use admin
db.createUser({
  user: "backend_service_user",
  pwd: "<DB_SERVICE_PW>",
  roles: [{ role: "readWrite", db: "its_db" }]
})
```

---

## Configuration Examples

### Minimal Development

```bash
ITS_ENV="development"
DB_SERVICE_PW="dev123"
DB_ROOT_PW="devroot123"
JWT_SECRET="dev_jwt_secret_32_characters_long"
USER_VERIFICATION_SECRET="dev_verify_secret_32_chars_long"
RESET_PWD_SECRET="dev_reset_secret_32_chars_long"
JUDGE0_MODE="local"
```

### Full Production

```bash
ITS_ENV="production"
DB_SERVICE_PW="Pr0d!Str0ng#Pass$123"
DB_ROOT_PW="R00t!V3ry#Str0ng$456"
JWT_SECRET="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
USER_VERIFICATION_SECRET="v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6"
RESET_PWD_SECRET="r1s2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6"
JUDGE0_MODE="local"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_SENDER="noreply@script-its.edu"
EMAIL_USR="script.its@gmail.com"
EMAIL_PWD="your_app_specific_password"
EMAIL_POSTFIX="@script-its.edu"
```

---

## References

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [MongoDB Connection String](https://docs.mongodb.com/manual/reference/connection-string/)
- [FastAPI Settings Management](https://fastapi.tiangolo.com/advanced/settings/)
- [Angular Environments](https://angular.io/guide/build#configuring-application-environments)
