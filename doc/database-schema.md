# Database Schema

## Overview

SCRIPT uses MongoDB as its primary database with the Beanie ODM for document modeling. The database name is `its_db`.

## Collections

### 1. users

Stores user accounts and authentication information.

**Schema:**
```python
{
  "_id": ObjectId,
  "email": str,                      # Hashed after verification
  "username": str,                   # Unique identifier
  "verification_email": str | None,  # Temporary, deleted after verification
  "encrypted_email": str | None,     # For password reset
  "hashed_password": str,            # bcrypt hashed
  "current_course": str,             # Active course unique_name
  "enrolled_courses": [str],         # List of enrolled course unique_names
  "register_datetime": {
    "date": str,
    "time": str
  },
  "settings": {
    "dataCollection": bool,          # Consent for detailed logging
    "consentForResearchUsage": bool  # Consent for research usage
  },
  "roles": [str] | None,            # Optional roles (admin, etc.)
  "is_active": bool,
  "is_verified": bool,
  "is_superuser": bool
}
```

**Indexes:**
- `email` (unique, case-insensitive)

**Key Features:**
- Email is hashed after verification for privacy
- `verification_email` field temporarily stores plaintext email
- Data collection preferences stored in `settings`
- Support for multiple course enrollment

---

### 2. courses

Stores course definitions and configurations.

**Schema:**
```python
{
  "_id": ObjectId,
  "unique_name": str,               # Course identifier
  "display_name": str,              # Human-readable name
  "domain": str,                    # Main topic (e.g., "Programming")
  "sub_domains": [str],             # Subtopics (e.g., ["Python", "Basics"])
  "curriculum": [str] | dict,       # List of task unique_names or structured curriculum
  "mandatory_curriculum": [str] | None,  # Required tasks
  "competencies": [str] | None,     # Skills taught
  "topics": [str] | None,           # Topic categories
  "default_topic": str | None,      # Default topic for task selection
  "course_settings": {              # Default settings (deprecated, use list)
    "feedback_init_time": int,
    "feedback_cooldown": int,
    "pedagogical_model": str,
    "language_generation_model": str
  } | None,
  "course_settings_list": [         # Settings for A/B testing
    {
      "pedagogical_model": str,     # e.g., "skipping_pfa", "state-space"
      "language_generation_model": str,
      "feedback_init_time": int,
      "feedback_cooldown": int
    }
  ],
  "sample_settings": [int],         # Distribution of settings (for random assignment)
  "q_matrix": dict | None,          # Skills x Tasks matrix for knowledge tracing
  "course_parameters": dict | None, # Model-specific parameters (PFA weights, etc.)
  "visibility": str                 # "student" | "admin"
}
```

**Indexes:**
- `unique_name` (unique)

**Key Features:**
- Supports multiple `course_settings_list` for experimental conditions
- `sample_settings` defines probability distribution for random assignment
- `q_matrix` maps tasks to required skills
- `course_parameters` stores PFA skill weights and other model parameters

---

### 3. course_enrollments

Tracks user enrollment in courses.

**Schema:**
```python
{
  "_id": ObjectId,
  "user_id": str,                   # Reference to users._id
  "username": str,                  # Denormalized for quick access
  "course_unique_name": str,        # Reference to courses.unique_name
  "tasks_completed": [str],         # List of completed task unique_names
  "tasks_attempted": [str],         # List of attempted task unique_names
  "completed": bool,                # Whether course is finished
  "course_settings_index": int      # Index into course.course_settings_list
}
```

**Indexes:**
- Composite: `(user_id, course_unique_name)` (unique)

**Key Features:**
- `course_settings_index` assigns user to experimental condition
- Tracks both attempted and completed tasks separately

---

### 4. tasks

Stores task definitions.

**Schema:**
```python
{
  "_id": ObjectId,
  "unique_name": str,               # Task identifier
  "display_name": str,              # Human-readable name
  "task": str,                      # Markdown description
  "example_solution": str,          # Model solution code
  "type": str,                      # "print" | "function" | "plot_function" | "multiple_choice"
  "tests": {                        # Unit tests for validation
    "test_1": {
      "input": str,
      "expected_output": str
    }
  },
  "prefix": str,                    # Code prefix for learner editor
  "arguments": [str] | None,        # Function arguments (for function tasks)
  "function_name": str | None,      # Expected function name
  "possible_choices": [str] | None, # Options (for multiple_choice)
  "correct_choices": [str] | None,  # Correct options
  "selected_choices": [str] | None, # User's selection
  "choice_explanations": [str] | None  # Explanations for each choice
}
```

**Indexes:**
- `unique_name` (unique)

**Task Types:**
1. **print**: Learner writes code that prints output
2. **function**: Learner implements a specific function
3. **plot_function**: Learner creates visualizations
4. **multiple_choice**: Learner selects from options

---

### 5. packed_state_spaces

Stores state spaces for state-space feedback models.

**Schema:**
```python
{
  "_id": ObjectId,
  "task_unique_name": str,          # Reference to tasks.unique_name
  "states": [                       # List of valid solution states
    {
      "state": str,                 # Code state
      "hashed_state": str | None,   # Hash for quick comparison
      "state_embedding": [float] | None  # Embedding vector for similarity
    }
  ],
  "adj_matrix": [[int]]             # Adjacency matrix (state transitions)
}
```

**Indexes:**
- `task_unique_name` (unique)

**Key Features:**
- Pre-computed state spaces for expert solutions
- Embeddings for semantic similarity matching
- Adjacency matrix defines valid transitions between states
- Used by state-space feedback pedagogical models

---

### 6. attempts

Tracks learner attempts at tasks with detailed state logging.

**Schema:**
```python
{
  "_id": ObjectId,
  "user_id": str,                   # Reference to users._id
  "task_unique_name": str,          # Reference to tasks.unique_name
  "course_unique_name": str,        # Reference to courses.unique_name
  "current_state": str,             # Latest code state
  "state_log": [                    # Detailed edit history
    {
      "diff": [                     # Line-level edit script
        ["I", line_num, content],   # Insertion
        ["D", line_num],            # Deletion
        ["R", line_num, [           # Replacement with char-level diff
          ["I", char_pos, char],
          ["D", char_pos],
          ["R", char_pos, char]
        ]]
      ],
      "timestamp": str,
      "code_length": int
    }
  ],
  "start_time_list": [str],         # Session start times
  "duration_list": [str]            # Session durations
}
```

**Indexes:**
- Composite: `(user_id, task_unique_name, course_unique_name)`

**Key Features:**
- Fine-grained edit tracking using edit distance (sed_backtrace)
- State log only stored if user consented to `dataCollection`
- Multiple sessions tracked with start times and durations
- Can reconstruct any previous code state from diffs

---

### 7. base_submissions

Base collection for all submission types (uses polymorphism).

**Schema:**
```python
{
  "_id": ObjectId,
  "user_id": str,
  "task_unique_name": str,
  "course_unique_name": str,
  "code": str,
  "type": str,                      # "test" | "run" | "feedback_request"
  "timestamp": str,
  "_class_id": str                  # Discriminator for inheritance
}
```

**Subclasses:**

#### tested_submissions
```python
{
  # ... base fields ...
  "type": "test",
  "results": [
    {
      "test_passed": bool,
      "expected_output": str,
      "actual_output": str,
      "error": str | None
    }
  ],
  "all_tests_passed": bool,
  "score": float
}
```

#### evaluated_run_code_submissions
```python
{
  # ... base fields ...
  "type": "run",
  "stdin": str,
  "stdout": str,
  "stderr": str,
  "exit_code": int,
  "status": str
}
```

#### evaluated_feedback_submissions
```python
{
  # ... base fields ...
  "type": "feedback_request",
  "feedback": str,
  "feedback_type": str,             # "llm" | "state_space"
  "model_used": str | None,
  "suggestions": [str],
  "matched_state": str | None       # For state-space feedback
}
```

**Indexes:**
- `(user_id, task_unique_name)`
- `timestamp`

---

### 8. surveys

Stores survey responses.

**Schema:**
```python
{
  "_id": ObjectId,
  "user_id": str,
  "survey_type": str,               # e.g., "learning_personality", "feedback"
  "responses": dict,                # Question-answer pairs
  "timestamp": str,
  "course_unique_name": str | None
}
```

---

### 9. app_settings

System-wide configuration (single document).

**Schema:**
```python
{
  "_id": ObjectId,
  "api_type": str,                  # "ollama" | "open-ai"
  "api_url": str,                   # LLM API endpoint
  "api_key": str | None,            # API key (if required)
  "email_host": str | None,
  "email_port": int | None,
  "email_sender": str | None,
  "email_enabled": bool
}
```

**Note:** This is a singleton collection with only one document.

---

### 10. global_account_list

Tracks all registered emails (hashed) to prevent duplicate accounts.

**Schema:**
```python
{
  "_id": ObjectId,
  "hashed_email_list": [str]        # List of hashed emails
}
```

---

## Relationships

```
User ─────┬───── CourseEnrollment ───── Course
          │
          ├───── Attempt ───── Task ───── PackedStateSpace
          │
          └───── Submission ───── Task
                 (Test/Run/Feedback)

Course ───── Tasks (via curriculum)
       ───── CourseSettings (embedded)
```

## Data Collection Levels

### Full Data Collection (user.settings.dataCollection = true)
- Complete `state_log` in attempts
- All submission details
- Timestamps for all actions
- Session durations

### Minimal Data Collection (user.settings.dataCollection = false)
- Only `current_state` in attempts (no edit history)
- Final submission results
- No intermediate states

## Indexes Strategy

### Performance Indexes:
- User lookups: `users.email`, `users.username`
- Course lookups: `courses.unique_name`
- Task lookups: `tasks.unique_name`
- Attempt queries: `(user_id, task_unique_name, course_unique_name)`
- Submission queries: `(user_id, task_unique_name)`

### Recommended Additional Indexes:
```javascript
// For analytics queries
db.submissions.createIndex({ timestamp: 1 })
db.attempts.createIndex({ "start_time_list.0": 1 })

// For user activity
db.course_enrollments.createIndex({ user_id: 1 })
db.submissions.createIndex({ user_id: 1, timestamp: -1 })
```

## Data Privacy

### PII Handling:
1. **Email**: Hashed after verification, original deleted
2. **Encrypted Email**: Used only for password reset
3. **Username**: Not considered PII (user-chosen pseudonym)
4. **Code/Submissions**: Considered educational data, not PII

### Consent Levels:
- **Data Collection**: Enables detailed state logging
- **Research Usage**: Permits use of anonymized data in publications

## Backup Strategy

Scripts available in `database_scripts/`:
- `backup_db.sh`: Create database backup
- `restore_collections.sh`: Restore from backup
- `download_backup.sh`: Download backup files

## Migration Considerations

### Schema Evolution:
- Use Beanie migrations for schema changes
- Maintain backward compatibility where possible
- Version control for course_parameters structure

### Future Enhancements:
1. Sharding strategy for large user bases
2. Time-series collection for analytics
3. Separate analytics database
4. Archive strategy for old attempts/submissions
