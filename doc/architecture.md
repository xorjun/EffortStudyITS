# System Architecture

## Overview

SCRIPT follows a modern three-tier architecture with a FastAPI backend, Angular frontend, MongoDB database, and external services for code execution and LLM-based feedback.

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │      Nginx        │
                   │  (Reverse Proxy)  │
                   └───────┬───┬───────┘
                           │   │
              ┌────────────┘   └────────────┐
              │                             │
    ┌─────────▼────────┐         ┌─────────▼────────┐
    │  Angular Frontend│         │  FastAPI Backend │
    │    (Port 4200)   │         │   (Port 8000)    │
    └──────────────────┘         └─────────┬────────┘
                                            │
                    ┌───────────────────────┼──────────────────┐
                    │                       │                  │
          ┌─────────▼─────────┐   ┌────────▼────────┐  ┌──────▼──────┐
          │     MongoDB        │   │     Judge0      │  │ LLM Server  │
          │   (Port 27017)     │   │  (Port 2358)    │  │  (Ollama/   │
          │                    │   │                 │  │   OpenAI)   │
          └────────────────────┘   └─────────────────┘  └─────────────┘
```

## Components

### 1. Frontend (Angular)

**Location**: `frontend/its_ui/`

The Angular application provides the user interface for the tutoring system.

#### Key Features:
- **Monaco Code Editor**: Integrated code editor with syntax highlighting
- **Task Display**: Markdown rendering for task descriptions
- **Feedback Panel**: Display results, errors, and AI-generated feedback
- **User Management**: Registration, login, profile management
- **Course Navigation**: Browse and switch between courses
- **Real-time State Tracking**: Monitors code changes for learning analytics

#### Technology:
- Angular (TypeScript)
- Monaco Editor
- Angular Material UI
- RxJS for reactive programming

### 2. Backend (FastAPI)

**Location**: `api/`

Python-based REST API handling all business logic, data persistence, and integration with external services.

#### Module Structure:

##### Core Modules

**`main.py`**: Application entry point
- FastAPI app initialization
- CORS middleware configuration
- Router registration
- Database initialization
- Background scheduler setup
- Request timeout middleware

**`config.py`**: Environment configuration
- Development/Production settings
- Database connection parameters
- Judge0 configuration
- Email settings
- LLM API configuration

##### Domain Modules

**`users/`**: User management
- FastAPI-Users integration
- JWT authentication
- Email verification
- Password reset
- User profile management
- Data collection consent

**`courses/`**: Course management
- Course creation and parsing
- Course enrollment
- Course settings per user/group
- Curriculum management
- Task parsing

**`tasks/`**: Task management
- Task CRUD operations
- Task metadata
- State spaces for feedback
- Task selection algorithms

**`attempts/`**: Learner attempt tracking
- Code state logging
- Edit distance computation (sed_backtrace)
- State compilation from diffs
- Session tracking
- Time tracking

**`submissions/`**: Code submission handling
- Unit test execution via Judge0
- Submission evaluation
- Result storage
- Performance tracking

**`feedback/`**: Feedback generation
- LLM-based feedback (Ollama/OpenAI)
- State-space feedback
- Feedback request handling
- Multiple feedback strategies

**`runs/`**: Code execution
- Custom parameter execution
- Judge0 integration
- Output capture
- Error handling

**`surveys/`**: Survey management
- Pre/post tests
- Learning personality surveys
- Custom survey handling

**`system/`**: System configuration
- Application settings
- About/Privacy/Imprint pages
- System information retrieval

##### Model Modules

**`models/`**: AI/ML models

```
models/
├── model_manager.py          # Model selection and management
├── domain/                   # Domain models
│   ├── feedback.py          # Feedback generation logic
│   └── skill_weights_pfa_update.py
├── knowledge_tracing/        # Learner modeling
│   ├── kt_base.py           # Base KT interface
│   └── pfa_model.py         # Performance Factor Analysis
└── pedagogical/              # Pedagogical strategies
    ├── base_pedagogical.py
    ├── content_selection/   # Task selection algorithms
    ├── prototype.py
    ├── skipping_tasks_pfa.py
    ├── llm_feedback_textual.py
    ├── llm_feedback_code.py
    ├── state_space_feedback.py
    └── study_2025/          # Research group configurations
```

##### Service Modules

**`services/`**: External service integrations

- **`language_generation.py`**: LLM integration
  - Ollama API client
  - OpenAI API client
  - Prompt management
  
- **`email_sending.py`**: Email notifications
  - Verification emails
  - Password reset emails
  - SMTP configuration

- **`text_embedding/`**: Text embeddings
  - Transformer-based embeddings
  - Similarity computations
  - Model caching

##### Database Module

**`db/`**: Database abstraction

- **`db_connector_beanie.py`**: Primary database interface
  - Beanie ODM operations
  - CRUD operations for all entities
  - Query helpers
  
- **`db_connector_motor.py`**: Low-level database access
  - Direct MongoDB queries
  - Bulk operations
  - Complex aggregations

### 3. Database (MongoDB)

**Database Name**: `its_db`

MongoDB stores all application data with the following collections:

#### Collections:

1. **users**: User accounts
   - Authentication credentials (hashed)
   - Profile information
   - Current course
   - Data collection preferences
   - Skills and competency levels

2. **courses**: Course definitions
   - Display name, domain, sub-domains
   - Curriculum (task list)
   - Course settings list (for A/B testing)
   - Validation status

3. **course_enrollments**: User-course relationships
   - User ID
   - Course unique name
   - Settings index (for group assignment)
   - Tasks attempted
   - Tasks completed

4. **tasks**: Task definitions
   - Unique name
   - Task type (print, function, multiple-choice)
   - Description (markdown)
   - Solution code
   - Unit tests
   - Skills required
   - State space (for feedback)

5. **attempts**: Learner attempts
   - User ID
   - Task unique name
   - State log (edit history)
   - Current state (code)
   - Start times
   - Durations

6. **submissions**: Code submissions
   - User ID
   - Task unique name
   - Submission type (test/run/feedback)
   - Code submitted
   - Results
   - Timestamp

7. **surveys**: Survey responses
   - User ID
   - Survey type
   - Responses
   - Timestamp

8. **app_settings**: System configuration
   - LLM API URL and key
   - API type (ollama/open-ai)
   - Email configuration
   - System-wide settings

### 4. Judge0 Service

**Purpose**: Secure code execution sandbox

Judge0 provides isolated code execution for:
- Running learner code with custom inputs
- Executing unit tests
- Capturing stdout/stderr
- Enforcing time/memory limits
- Supporting multiple languages (primarily Python)

#### Components:
- **j0-server**: API server (port 2358)
- **j0-workers**: Execution workers
- **Configuration**: `judge0/judge0.conf`

#### Modes:
- **Local**: Self-hosted Judge0 instance
- **Remote**: External Judge0 service (requires API token)

### 5. LLM Server (Optional)

**Purpose**: AI-generated feedback

#### Supported APIs:
1. **Ollama**: Self-hosted LLM server
   - Location: `llm-server/`
   - Models: qwen3-coder:30b (default)
   - Local deployment

2. **OpenAI**: External API
   - GPT models
   - Requires API key

#### Usage:
- Textual feedback on code
- Code-specific feedback
- Error explanations
- Conceptual hints

## Data Flow

### 1. User Registration & Login

```
User → Frontend → Backend → MongoDB
                    ↓
              Email Service
                    ↓
               User Email
```

1. User submits registration form
2. Backend creates user with hashed password
3. Verification email sent
4. User verifies via email link
5. User logs in with JWT

### 2. Task Solving Flow

```
User → Frontend → Backend → MongoDB (get task)
                    ↓
          Task Selector Model
                    ↓
             Frontend (display)
                    ↓
         User writes code
                    ↓
    Backend (track attempts) → MongoDB
```

### 3. Code Submission Flow

```
User → Frontend → Backend → Judge0 (execute tests)
                    ↓           ↓
                 MongoDB    Results
                    ↓           ↓
            Knowledge Tracing  Frontend
                    ↓
            Update Skills
```

### 4. Feedback Request Flow

```
User → Frontend → Backend → Pedagogical Model
                    ↓
              LLM Server / State Space
                    ↓
             Generate Feedback
                    ↓
    MongoDB (store) → Frontend (display)
```

## Security

### Authentication
- JWT tokens for API authentication
- Email verification required
- Password hashing (bcrypt via FastAPI-Users)
- Secure password reset flow

### Data Protection
- User consent for data collection
- Email encryption and hashing
- Secure MongoDB credentials
- Environment variable management

### Code Execution
- Isolated Judge0 sandboxes
- Resource limits (time, memory)
- No network access from executed code

## Scalability Considerations

### Current Architecture:
- Single MongoDB instance
- Stateless FastAPI backend (horizontally scalable)
- Nginx load balancing capable
- Docker containerization

### Potential Improvements:
- MongoDB replica sets for HA
- Redis for session caching
- Message queue for background tasks
- CDN for static assets
- Horizontal scaling of backend workers

## Monitoring & Logging

### Current Implementation:
- Docker JSON file logging (100MB max)
- Application logs to stdout
- MongoDB query logging
- APScheduler task logging

### Recommendations:
- Implement structured logging (ELK stack)
- Add APM (Application Performance Monitoring)
- Set up alerts for errors
- Dashboard for system metrics

## Environment Modes

### Development
- `ITS_ENV=development`
- Local MongoDB
- No email sending
- Detailed error messages

### Development-Docker
- `ITS_ENV=development-docker`
- Docker-based MongoDB
- Judge0 in Docker
- Full stack containerized

### Production
- `ITS_ENV=production`
- All services containerized
- Email enabled
- Reduced logging verbosity
- Security hardened

## Performance Optimizations

1. **Database Indexing**: Strategic indexes on frequently queried fields
2. **Model Caching**: Pedagogical models cached in memory
3. **Embedding Model**: Singleton pattern for transformer models
4. **Connection Pooling**: Motor for MongoDB async connections
5. **APScheduler**: Background tasks for non-blocking operations
6. **Request Timeout**: 45-second middleware timeout
