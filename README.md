# EffortStudyITS (ITS03)

**A modified version of the SCRIPT Intelligent Tutoring System, adapted to conduct the Effort Study at Bielefeld University.**

This platform provides an online Python code-editor with step-based feedback, automated unit-test evaluation, and competency-based task selection — extended with study-specific instrumentation for research data collection.

> **Base project:** [SCRIPT](https://gitlab.ub.uni-bielefeld.de/publications-ag-kml/script) — Step-based Coding for Research and Interactive Programming Training, developed and maintained by the Knowledge Representation and Machine Learning (KML) group of Bielefeld University (https://www.uni-bielefeld.de/fakultaeten/technische-fakultaet/arbeitsgruppen/kml/).

---

## Quick Start (Docker)

The fastest way to get the platform running:

```bash
git clone https://github.com/xorjun/EffortStudyITS.git
cd EffortStudyITS
```

Create a `.env` file in the project root:

```env
ITS_ENV=development-docker
DB_SERVICE_PW=your_db_password
DB_ROOT_PW=your_root_password
JWT_SECRET=your_jwt_secret
USER_VERIFICATION_SECRET=your_verification_secret
RESET_PWD_SECRET=your_reset_secret
JUDGE0_MODE=local
```

Start all services:

```bash
docker compose up -d
```

The platform will be available at `http://localhost:8080` (frontend) and `http://localhost:8888/api` (backend).

---

## Local Development Setup

### Prerequisites

- **Python 3.11+** with [`uv`](https://docs.astral.sh/uv/) (package manager)
- **MongoDB 5.x** running on `localhost:27017`
- **Node.js 20+** with Angular CLI 19
- **Docker** (for Judge0 code execution)

### 1. Backend Setup

```bash
cd api

# Install dependencies via uv (fast, reproducible)
uv sync

# Run the backend
uv run python main.py
```

The backend starts on `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd frontend/its_ui

# Install dependencies
npm install

# Start dev server
ng serve
```

The frontend starts on `http://localhost:4200` and proxies API requests to the backend.

### 3. Database Setup

Create a MongoDB user with read/write access to the `its_db` database:

```js
use admin
db.createUser({
  user: "backend_service_user",
  pwd: "your_db_password",
  roles: [{ role: "readWrite", db: "its_db" }]
})
```

### 4. Judge0 (Code Execution)

```bash
cd judge0
docker compose up -d
```

### 5. LLM Server (Optional — for AI feedback)

```bash
cd llm-server
docker compose up -d
```

Or point to an external Ollama instance via the admin settings UI.

---

## Creating Users

### First Admin User

1. Register a new account through the UI at `/auth/register`.
2. In development mode, the verification token is printed to the backend console — look for the link in the terminal running `uv run python main.py`.
3. Visit the verification link to activate the account.
4. Connect to MongoDB and add the `admin` role:

```js
use its_db
db.User.updateOne(
  { email: "your_email@example.com" },
  { $set: { roles: ["admin"] } }
)
```

5. Log in — the admin settings panel is now accessible from the navigation bar.

### Creating Regular Users

Users self-register at `/auth/register`. In production (with email configured), a verification email is sent. In development, the verification link appears in the backend logs.

### Pre-configured Test Users

The platform includes a database setup script at `database_scripts/setup_users.py` for creating test accounts in bulk.

---

## Using the Platform

### Admin: Loading Courses

1. Log in as an admin user.
2. From the course selection page, click **"Upload Course"**.
3. Select a course folder (structured per `courses/course_template/`).
4. The course appears for all enrolled users.

### Admin: Configuring Settings

Navigate to the admin settings panel from the navigation bar:
- **LLM API** — configure the Ollama endpoint for AI-generated feedback
- **Pedagogical Model** — select feedback strategy (LLM-based, state-space, etc.)
- **Editor Policy** — toggle copy/paste restrictions for the code editor
- **Email Whitelist** — restrict registration to specific domains

### Learner: Solving Tasks

1. Select a course from the course selection page.
2. Read the task description (upper-left panel).
3. Write your solution in the Monaco code editor (right panel).
4. Use the action buttons:
   - **Run** — execute your code with custom parameters
   - **Submit** — run unit tests and see results
   - **Feedback** — request AI-generated step-by-step guidance

### Learner: Tracking Progress

The **skill overview** (navigation bar) shows competency estimates across course topics, updated after each submission.

---

## Project Structure

```
EffortStudyITS/
├── api/                    # FastAPI backend
│   ├── main.py             # Application entrypoint
│   ├── pyproject.toml      # uv dependency spec
│   ├── uv.lock             # Locked dependencies
│   ├── models/             # Pedagogical, domain & learner models
│   ├── attempts/           # Code attempt tracking
│   ├── courses/            # Course loading & parsing
│   ├── db/                 # MongoDB connector (Beanie ODM)
│   ├── feedback/           # Feedback generation pipeline
│   ├── runs/               # Code execution (Judge0)
│   ├── services/           # Email, LLM, embeddings
│   ├── skills/             # Competency estimation (PFA)
│   ├── submissions/        # Unit-test evaluation
│   ├── surveys/            # In-platform surveys
│   ├── system/             # Admin settings & info pages
│   ├── tasks/              # Task schemas & state spaces
│   ├── tests/              # Pytest test suite
│   └── users/              # Auth & user management
├── frontend/               # Angular 19 frontend
│   └── its_ui/src/app/     # Components, services, shared modules
├── courses/                # Course content (tasks, tests, markdown)
├── judge0/                 # Judge0 code execution engine
├── llm-server/             # Ollama LLM server config
├── appwrite/               # Study management cloud functions
├── database_scripts/       # DB setup & migration scripts
├── doc/                    # Architecture & API documentation
├── docker-compose.yml      # Full-stack Docker deployment
└── nginx.conf              # Reverse proxy config
```

---

## Adding New Courses

Create a folder under `courses/` with this structure:

```
my_course/
├── course.json             # Course metadata & competency definitions
├── introduction.md         # Welcome page shown to learners
└── task_folder/
    └── task_my_task/
        ├── task.json       # Task type, parameters, hints
        ├── task.md         # Task description (Markdown)
        ├── example_solution.py
        └── test_my_task.py # Unit tests for auto-grading
```

Use `courses/course_template/` as a reference.



---

## License

"SCRIPT" is an Intelligent Tutoring System for Programming.
Copyright (C) 2025  Benjamin Paaßen, Jesper Dannath, Alina Deriyeva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Contributing

We welcome external contributors to this project. If you want to contribute, we are happy to assist with questions regarding the integration of your contribution with our system. In any case, contributions should align with the general system architecture.

## Contributors

### Active Contributors

- Alina Deriyeva (primary)
- Arno Gaußelmann
- Benjamin Paaßen
- Jesper Dannath (primary)

### Additional Contributors

- Aliena Strathmann
- Björn Buschkämper
- Tobias Hillmer
