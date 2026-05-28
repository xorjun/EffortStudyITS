# API Reference

## Base URL

All API endpoints are prefixed with `/api`

**Local Development**: `http://localhost:8888/api`  
**Production**: `https://your-domain.com/api`

## Interactive Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **OpenAPI Schema**: `/api/openapi.json`

## Authentication

Most endpoints require authentication via JWT tokens.

### Headers
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### POST `/api/auth/jwt/login`
Login and obtain JWT token

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

#### POST `/api/auth/register`
Register new user

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "string",
  "password": "string",
  "is_verified": false,
  "settings": {
    "dataCollection": true,
    "consentForResearchUsage": true
  }
}
```

**Response:** `UserRead` object

#### POST `/api/auth/forgot-password`
Request password reset

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### POST `/api/auth/reset-password`
Reset password with token

**Request Body:**
```json
{
  "token": "string",
  "password": "string"
}
```

#### POST `/api/auth/request-verify-token`
Request email verification

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### POST `/api/auth/verify`
Verify email with token

**Request Body:**
```json
{
  "token": "string"
}
```

---

## User Management

#### GET `/api/users/me`
Get current user profile

**Authentication:** Required

**Response:**
```json
{
  "id": "string",
  "email": "string",
  "username": "string",
  "current_course": "string",
  "settings": {
    "dataCollection": true,
    "consentForResearchUsage": true
  },
  "skills": {}
}
```

#### PATCH `/api/users/me`
Update current user

**Authentication:** Required

**Request Body:**
```json
{
  "settings": {
    "dataCollection": false
  }
}
```

---

## Course Management

#### GET `/api/info`
Get all available courses

**Authentication:** Required

**Response:**
```json
[
  {
    "unique_name": "intro_py",
    "display_name": "Introduction to Python",
    "domain": "Programming",
    "sub_domains": ["Python", "Basics"],
    "task_count": 25
  }
]
```

#### GET `/api/get/{course_unique_name}`
Get course details

**Authentication:** Required

**Path Parameters:**
- `course_unique_name`: Course identifier

**Response:**
```json
{
  "unique_name": "intro_py",
  "display_name": "Introduction to Python",
  "domain": "Programming",
  "sub_domains": ["Python", "Basics"],
  "curriculum": ["task_1", "task_2"],
  "course_settings_list": [
    {
      "pedagogical_model": "skipping_pfa",
      "task_selector": "adaptive"
    }
  ]
}
```

#### POST `/api/select`
Select/enroll in a course

**Authentication:** Required

**Request Body:**
```json
{
  "course_unique_name": "intro_py"
}
```

**Response:**
```json
{
  "status": "enrolled",
  "course_unique_name": "intro_py",
  "course_settings_index": 0
}
```

#### GET `/api/get_settings/{course_unique_name}`
Get course settings for user

**Authentication:** Required

**Path Parameters:**
- `course_unique_name`: Course identifier

**Response:**
```json
{
  "pedagogical_model": "skipping_pfa",
  "task_selector": "adaptive",
  "feedback_enabled": true,
  "llm_model": "qwen3-coder:30b"
}
```

#### POST `/api/update_settings`
Update course settings (admin)

**Authentication:** Required (admin)

**Request Body:**
```json
{
  "course_unique_name": "intro_py",
  "settings": {
    "pedagogical_model": "state-space"
  }
}
```

#### POST `/api/update_tasks`
Update course tasks (admin)

**Authentication:** Required (admin)

---

## Task Management

#### GET `/api/task/for_user/`
Get next recommended task for user

**Authentication:** Required

**Query Parameters:**
- `topic` (optional): Filter by topic

**Response:**
```json
{
  "unique_name": "print_hello",
  "display_name": "Print Hello World",
  "description": "# Task Description\n\nWrite a program...",
  "task_type": "print",
  "solution": "print('Hello World')",
  "skills": ["python_basics", "print_function"]
}
```

#### GET `/api/task/for_user/{topic}`
Get task for specific topic

**Authentication:** Required

**Path Parameters:**
- `topic`: Topic identifier

#### GET `/api/task/by_name/{unique_name}`
Get specific task by name

**Authentication:** Required

**Path Parameters:**
- `unique_name`: Task identifier

**Response:** Same as task object above, plus:
```json
{
  "unit_tests": [
    {
      "input": "",
      "expected_output": "Hello World\n"
    }
  ],
  "state_space": {
    "states": [...],
    "transitions": [...]
  }
}
```

---

## Attempt Management

#### GET `/api/attempt/get_state/{task_unique_name}`
Get or create attempt for task

**Authentication:** Required

**Path Parameters:**
- `task_unique_name`: Task identifier

**Response:**
```json
{
  "attempt_id": "string",
  "code": "# Previous code state"
}
```

#### POST `/api/attempt/update_state`
Update attempt state (code changes)

**Authentication:** Required

**Request Body:**
```json
{
  "attempt_id": "string",
  "task_unique_name": "string",
  "line_update": [[line_number, "new_code"]],
  "code_length": 150,
  "timestamp": "01.01.2025 12:00:00"
}
```

**Response:**
```json
{
  "status": "success",
  "attempt_id": "string"
}
```

---

## Code Submission & Execution

#### POST `/api/submit`
Submit code for evaluation

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": "string",
  "task_unique_name": "string",
  "code": "print('Hello World')",
  "type": "test"
}
```

**Response:**
```json
{
  "submission_id": "string",
  "status": "completed",
  "results": [
    {
      "test_passed": true,
      "expected_output": "Hello World\n",
      "actual_output": "Hello World\n",
      "error": null
    }
  ],
  "all_tests_passed": true,
  "score": 1.0
}
```

#### POST `/api/run/run_code`
Run code with custom input

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": "string",
  "task_unique_name": "string",
  "code": "name = input('Name: ')\\nprint(f'Hello {name}')",
  "stdin": "Alice"
}
```

**Response:**
```json
{
  "submission_id": "string",
  "stdout": "Name: Hello Alice\n",
  "stderr": "",
  "status": "completed",
  "exit_code": 0
}
```

#### POST `/api/mark_solved/{task_unique_name}`
Mark task as solved

**Authentication:** Required

**Path Parameters:**
- `task_unique_name`: Task identifier

**Response:**
```json
{
  "status": "marked_solved",
  "task_unique_name": "string"
}
```

#### GET `/api/submission/feedback/{submission_id}`
Get submission feedback

**Authentication:** Required

**Path Parameters:**
- `submission_id`: Submission identifier

**Response:**
```json
{
  "submission_id": "string",
  "feedback": "Your code is correct but could be improved...",
  "feedback_type": "llm",
  "suggestions": []
}
```

---

## Feedback System

#### POST `/api/feedback`
Request AI feedback on code

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": "string",
  "task_unique_name": "string",
  "code": "print('Hello')",
  "context": "I'm stuck on this task"
}
```

**Response:**
```json
{
  "feedback_id": "string",
  "feedback": "Your code prints 'Hello' but the task requires...",
  "feedback_type": "llm",
  "model_used": "qwen3-coder:30b",
  "suggestions": [
    "Try using an f-string",
    "Check the expected output"
  ]
}
```

---

## Survey Management

#### POST `/api/surveys/submit`
Submit survey response

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": "string",
  "survey_type": "learning_personality",
  "responses": {
    "question_1": "answer_1",
    "question_2": "answer_2"
  }
}
```

**Response:**
```json
{
  "survey_id": "string",
  "status": "submitted"
}
```

---

## System Settings

#### GET `/api/settings/get`
Get system settings (admin)

**Authentication:** Required (admin)

**Response:**
```json
{
  "api_type": "ollama",
  "api_url": "http://llm-server:11434/",
  "api_key": null,
  "email_enabled": true
}
```

#### POST `/api/settings/update`
Update system settings (admin)

**Authentication:** Required (admin)

**Request Body:**
```json
{
  "api_type": "open-ai",
  "api_url": "https://api.openai.com/v1/",
  "api_key": "sk-..."
}
```

---

## System Information

#### GET `/api/info/about`
Get about page content

**Response:** Markdown content

#### GET `/api/info/data_collection`
Get data collection policy

**Response:** Markdown content

#### GET `/api/info/privacy_policy`
Get privacy policy

**Response:** Markdown content

#### GET `/api/info/imprint`
Get imprint

**Response:** Markdown content

---

## Data Models

### User
```typescript
{
  id: string;
  email: string;
  username: string;
  current_course: string;
  settings: {
    dataCollection: boolean;
    consentForResearchUsage: boolean;
  };
  skills: Record<string, number>;
  is_active: boolean;
  is_verified: boolean;
}
```

### Course
```typescript
{
  unique_name: string;
  display_name: string;
  domain: string;
  sub_domains: string[];
  curriculum: string[];
  course_settings_list: CourseSettings[];
}
```

### Task
```typescript
{
  unique_name: string;
  display_name: string;
  description: string;
  task_type: 'print' | 'function' | 'multiple_choice';
  solution: string;
  unit_tests: UnitTest[];
  skills: string[];
  state_space?: StateSpace;
}
```

### Attempt
```typescript
{
  id: string;
  user_id: string;
  task_unique_name: string;
  course_unique_name: string;
  current_state: string;
  state_log: AttemptState[];
  start_time_list: string[];
  duration_list: string[];
}
```

### Submission
```typescript
{
  id: string;
  user_id: string;
  task_unique_name: string;
  code: string;
  type: 'test' | 'run' | 'feedback_request';
  results: TestResult[];
  timestamp: string;
  all_tests_passed?: boolean;
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Common Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error
- `504`: Gateway Timeout (> 45 seconds)

### Validation Error Example
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production deployments.

## Versioning

API is currently unversioned. All endpoints are at `/api/*`. Future versions may use `/api/v2/*` etc.

## WebSocket Support

Not currently implemented. All communication is via REST API.

## Pagination

Large list endpoints currently return all results. Future implementations may include:
- Query parameters: `?page=1&limit=50`
- Response headers: `X-Total-Count`, `X-Page`, `X-Per-Page`
