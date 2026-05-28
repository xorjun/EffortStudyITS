# Course Structure Documentation

## Overview

Courses in SCRIPT are defined using JSON configuration files and markdown task descriptions. Each course consists of a curriculum, task definitions, and pedagogical settings.

---

## Course Directory Structure

```
courses/
├── my_course/
│   ├── course.json              # Course configuration
│   └── task_folder/             # Task definitions
│       ├── task_print_hello/
│       │   ├── task.md          # Task description (markdown)
│       │   ├── example_solution.py
│       │   └── test_*.py        # Unit tests
│       ├── task_for_loop/
│       │   ├── task.md
│       │   ├── example_solution.py
│       │   └── test_*.py
│       └── ...
```

---

## Course Configuration (course.json)

### Basic Structure

```json
{
  "display_name": "Introduction to Python",
  "unique_name": "intro_py",
  "domain": "Programming",
  "sub_domains": ["Python", "Basics"],
  "curriculum": ["task_1", "task_2", "task_3"],
  "course_settings_list": [
    {
      "pedagogical_model": "skipping_pfa",
      "language_generation_model": "qwen3-coder:30b",
      "feedback_init_time": 60,
      "feedback_cooldown": 30
    }
  ],
  "sample_settings": [1]
}
```

### Field Descriptions

#### Required Fields

**`display_name`** (string)
- Human-readable course name
- Displayed in UI
- Example: "Introduction to Python"

**`unique_name`** (string)
- Unique identifier for the course
- Used in database and API calls
- Convention: lowercase, underscores
- Example: "intro_py"

**`domain`** (string)
- Main subject area
- Examples: "Programming", "Data Science", "Algorithms"

**`sub_domains`** (array of strings)
- Subcategories or topics
- Examples: ["Python", "Basics"], ["Machine Learning", "NumPy"]

**`curriculum`** (array or object)
- List of task unique names in order
- Can be simple array or structured by topics

**Simple curriculum (array):**
```json
"curriculum": ["task_1", "task_2", "task_3"]
```

**Structured curriculum (object):**
```json
"curriculum": {
  "basics": ["print_hello", "variables"],
  "control_flow": ["if_else", "for_loop"],
  "functions": ["define_function", "return_value"]
}
```

#### Optional Fields

**`mandatory_curriculum`** (array)
- Tasks that cannot be skipped by adaptive models
- Example: `["introduction_task", "final_exam"]`

**`competencies`** (array)
- Skills taught in the course
- Used by PFA model
- Example: `["python_basics", "loops", "functions", "conditionals"]`

**`topics`** (array)
- Topic categories for task grouping
- Example: `["Basics", "Control Flow", "Functions", "Data Structures"]`

**`default_topic`** (string)
- Default topic for task selection
- Example: `"Basics"`

**`visibility`** (string)
- Who can see the course
- Values: `"student"` (default) or `"admin"`

**`q_matrix`** (object)
- Maps tasks to required skills (for PFA model)
- Automatically generated if not provided

```json
"q_matrix": {
  "task_1": [1, 0, 0, 0],  // Requires skill 0 only
  "task_2": [1, 1, 0, 0],  // Requires skills 0 and 1
  "task_3": [0, 1, 1, 0]   // Requires skills 1 and 2
}
```

**`course_parameters`** (object)
- Model-specific parameters
- For PFA: skill weights

```json
"course_parameters": {
  "skill_weights_pfa": [0.5, -0.3, -1.0, 0.6, -0.4, -0.8]
}
```

### Course Settings

**`course_settings_list`** (array)
- Multiple settings for A/B testing
- Each entry is a complete settings object

```json
"course_settings_list": [
  {
    "pedagogical_model": "skipping_pfa",
    "language_generation_model": "qwen3-coder:30b",
    "feedback_init_time": 60,
    "feedback_cooldown": 30
  },
  {
    "pedagogical_model": "state-space",
    "language_generation_model": "default",
    "feedback_init_time": 30,
    "feedback_cooldown": 15
  }
]
```

**Settings Fields:**

- **`pedagogical_model`**: Model name (see [Models Documentation](models.md))
  - `"skipping_pfa"` (default)
  - `"state-space"`
  - `"prototype"`
  - `"group_A"`, `"group_B"`, etc.

- **`language_generation_model`**: LLM model for feedback
  - `"qwen3-coder:30b"` (default)
  - `"codellama:13b"`
  - `"gpt-4"` (if using OpenAI)
  - `"default"` (uses system default)

- **`feedback_init_time`**: Seconds before feedback button appears
  - Prevents immediate requests
  - Example: `60` (1 minute)

- **`feedback_cooldown`**: Seconds between feedback requests
  - Prevents spam
  - Example: `30` (30 seconds)

**`sample_settings`** (array of integers)
- Distribution for random assignment
- Length must match `course_settings_list`
- Values are weights for each setting

```json
"sample_settings": [1, 1]  // 50/50 split between two settings
"sample_settings": [2, 1]  // 2/3 get setting 0, 1/3 get setting 1
```

---

## Task Structure

### Task Directory

Each task has its own directory:

```
task_folder/
└── task_unique_name/
    ├── task.md                    # Task description (required)
    ├── example_solution.py        # Solution code (required)
    ├── test_*.py                  # Unit tests (required for function/print tasks)
    └── images/                    # Optional images
        └── diagram.png
```

### Task Description (task.md)

Markdown file with task instructions.

**Example:**

```markdown
# Print Hello World

Write a Python program that prints "Hello, World!" to the console.

## Requirements

- Use the `print()` function
- Output must match exactly: "Hello, World!"

## Example Output

\`\`\`
Hello, World!
\`\`\`

## Hints

- Remember to use quotation marks for strings
- Pay attention to capitalization and punctuation
```

**Supported Markdown Features:**

- Headers (`#`, `##`, `###`)
- Paragraphs
- Code blocks with syntax highlighting
- Inline code (`` `code` ``)
- Math equations (LaTeX): `$ inline $` or `$$ block $$`
- Lists (ordered and unordered)
- Bold and italic
- Images: `![alt text](./images/diagram.png)`

### Solution File (example_solution.py)

Contains the model solution.

**Print Task Example:**
```python
# example_solution.py
print("Hello, World!")
```

**Function Task Example:**
```python
# example_solution.py
def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}!"
```

**Multiple Choice Task:**
Not required for multiple choice tasks.

### Unit Tests (test_*.py)

Test files define the expected behavior.

#### Print Task Tests

**File naming:** `test_print_*.py` or `test_<task_name>.py`

```python
# test_print_hello.py

tests = {
    "test_1": {
        "input": "",
        "expected_output": "Hello, World!\n"
    }
}
```

**With Input:**
```python
# test_print_greet.py

tests = {
    "test_1": {
        "input": "Alice",
        "expected_output": "Hello, Alice!\n"
    },
    "test_2": {
        "input": "Bob",
        "expected_output": "Hello, Bob!\n"
    }
}
```

#### Function Task Tests

**File naming:** `test_function_*.py`

```python
# test_function_square.py

tests = {
    "test_1": {
        "function_name": "square",
        "args": [2],
        "expected_output": 4
    },
    "test_2": {
        "function_name": "square",
        "args": [5],
        "expected_output": 25
    },
    "test_3": {
        "function_name": "square",
        "args": [-3],
        "expected_output": 9
    }
}
```

**Testing Exceptions:**
```python
tests = {
    "test_error": {
        "function_name": "divide",
        "args": [10, 0],
        "expected_error": "ZeroDivisionError"
    }
}
```

#### Multiple Choice Tests

Not applicable. Correctness is checked directly against `correct_choices`.

---

## Task Types

### 1. Print Task

Student writes code that prints output.

**Characteristics:**
- No function definition required
- Output captured from stdout
- Tests compare printed output

**Task Unique Name Convention:** `task_<name>` (no special prefix)

**Example:** See "Print Task Tests" above

### 2. Function Task

Student implements a specific function.

**Characteristics:**
- Function name specified
- Arguments passed to function
- Return value checked

**Task Unique Name Convention:** `task_<name>` (parser auto-detects)

**Metadata (auto-generated):**
```json
{
  "type": "function",
  "function_name": "square",
  "arguments": ["x"]
}
```

### 3. Plot Function Task

Student creates visualizations using matplotlib.

**Characteristics:**
- Similar to function task
- Function should return matplotlib figure
- Visual comparison possible

**Task Unique Name Convention:** `task_<name>`

**Example:**
```python
# example_solution.py
import matplotlib.pyplot as plt

def plot_line(x, y):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    return fig
```

### 4. Multiple Choice Task

Student selects correct options from a list.

**Characteristics:**
- No code writing
- No solution file needed
- No test file needed

**Task Directory:**
```
task_mc_python_basics/
└── task.md
```

**Task Markdown Format:**
```markdown
# Python Basics Quiz

Which of the following are valid Python variable names?

## Choices

- [x] `my_variable`
- [x] `_private`
- [ ] `2fast`
- [ ] `class`
- [x] `myVar2`

## Explanation

Variable names cannot start with a digit and cannot be Python keywords.
```

**Format:**
- `[x]`: Correct choice
- `[ ]`: Incorrect choice

---

## Creating a New Course

### Step 1: Create Course Directory

```bash
cd courses
mkdir my_new_course
cd my_new_course
```

### Step 2: Create course.json

```json
{
  "display_name": "My New Course",
  "unique_name": "my_new_course",
  "domain": "Programming",
  "sub_domains": ["Python"],
  "curriculum": ["task_1"],
  "course_settings_list": [
    {
      "pedagogical_model": "skipping_pfa",
      "language_generation_model": "default",
      "feedback_init_time": 60,
      "feedback_cooldown": 30
    }
  ],
  "sample_settings": [1]
}
```

### Step 3: Create Task Directory

```bash
mkdir -p task_folder/task_1
cd task_folder/task_1
```

### Step 4: Create task.md

```markdown
# Task 1: Print Your Name

Write a program that prints your name.

## Example Output

\`\`\`
John Doe
\`\`\`
```

### Step 5: Create example_solution.py

```python
print("John Doe")
```

### Step 6: Create test_*.py

```python
# test_print_name.py

tests = {
    "test_1": {
        "input": "",
        "expected_output": "John Doe\n"
    }
}
```

### Step 7: Upload Course

**Via UI:**
1. Log in as admin/tutor
2. Go to course selection
3. Click "Upload Course"
4. Select `my_new_course` folder

**Via Command Line:**
```bash
# Copy to backend
cp -r my_new_course /path/to/script/api/courses/

# Restart backend
docker-compose restart fastapi-backend
```

---

## Advanced Features

### Competencies and Q-Matrix

For PFA-based adaptive tutoring:

**1. Define Competencies:**
```json
"competencies": ["basics", "loops", "conditionals", "functions"]
```

**2. Create Q-Matrix:**
```json
"q_matrix": {
  "task_hello": [1, 0, 0, 0],
  "task_for_loop": [1, 1, 0, 0],
  "task_if_else": [1, 0, 1, 0],
  "task_factorial": [1, 1, 1, 1]
}
```

**3. Initialize Weights (optional):**
```json
"course_parameters": {
  "skill_weights_pfa": [
    0.5, -0.3, -1.0,   // skill 0: success, failure, bias
    0.6, -0.4, -0.8,   // skill 1
    0.7, -0.2, -0.9,   // skill 2
    0.8, -0.1, -1.0    // skill 3
  ]
}
```

If not provided, default weights are generated and updated automatically.

### State Spaces for Feedback

For state-space feedback models:

**1. Create state space file:**
```python
# In task_folder/task_1/
# state_space.json
{
  "states": [
    {
      "state": "print('Hello')",
      "hashed_state": "hash1"
    },
    {
      "state": "print('Hello, World!')",
      "hashed_state": "hash2"
    }
  ],
  "adj_matrix": [[0, 1], [0, 0]]
}
```

**2. Or generate automatically:**
State spaces can be auto-generated from solution variants.

### Images in Tasks

**1. Create images directory:**
```bash
mkdir task_folder/task_1/images
```

**2. Add image files:**
```bash
cp diagram.png task_folder/task_1/images/
```

**3. Reference in markdown:**
```markdown
![Diagram](./images/diagram.png)
```

---

## Course Validation

Before deployment, validate your course:

```python
from models.model_manager import model_manager
from db import database

course = await database.get_course("my_new_course")
status, error = model_manager.validate_course(course)

if status == "valid":
    print("Course is valid!")
else:
    print(f"Course validation failed: {error}")
```

**Validation Checks:**
- All curriculum tasks exist
- Q-matrix matches curriculum (if PFA model)
- Competencies match Q-matrix dimensions
- Skill weights match competencies
- Test files are properly formatted
- Solution files exist

---

## Best Practices

1. **Task Naming:**
   - Use descriptive, unique names
   - Convention: `task_<action>_<object>`
   - Examples: `task_print_hello`, `task_sort_list`

2. **Task Descriptions:**
   - Clear and concise
   - Include examples
   - Specify requirements explicitly

3. **Test Coverage:**
   - Test edge cases
   - Include at least 3 tests per task
   - Test error conditions if applicable

4. **Curriculum Order:**
   - Start simple, increase difficulty
   - Build on previous concepts
   - Group related tasks by topic

5. **Competencies:**
   - Keep granularity balanced (4-10 skills)
   - Make skills orthogonal
   - Align with learning objectives

6. **Course Settings:**
   - Start with conservative feedback times
   - Test with pilot users
   - Monitor engagement metrics

---

## Troubleshooting

### Course Not Appearing

- Check `visibility` field (set to `"student"`)
- Verify course uploaded correctly
- Restart backend

### Tasks Not Loading

- Verify task names in `curriculum` match directory names
- Check for typos
- Ensure `task.md` and `example_solution.py` exist

### Tests Failing Unexpectedly

- Check test format (dict with `test_1`, `test_2`, etc.)
- Verify expected output includes newlines for print tasks
- Test solution file manually

### PFA Model Errors

- Run course validation
- Ensure Q-matrix dimensions match competencies
- Regenerate weights if course changed

### State-Space Feedback Not Working

- Verify state space file exists
- Check state embeddings are computed
- Ensure task type is compatible

---

## Examples

See example courses in `courses/` directory:
- `test_course/`: Minimal example
- `Intro_to_PY/`: Full Python introduction
- `Intro_to_ML/`: Machine learning course
- `course_template/`: Template for new courses

---

## Tools

### Course Generator Script

```python
# tools/generate_course.py
import json
import os

def create_course(name, display_name, num_tasks):
    # Create course structure
    os.makedirs(f"courses/{name}/task_folder", exist_ok=True)
    
    # Create course.json
    course = {
        "display_name": display_name,
        "unique_name": name,
        "domain": "Programming",
        "sub_domains": [],
        "curriculum": [f"task_{i}" for i in range(1, num_tasks + 1)],
        "course_settings_list": [{
            "pedagogical_model": "skipping_pfa",
            "language_generation_model": "default",
            "feedback_init_time": 60,
            "feedback_cooldown": 30
        }],
        "sample_settings": [1]
    }
    
    with open(f"courses/{name}/course.json", "w") as f:
        json.dump(course, f, indent=2)
    
    # Create task templates
    for i in range(1, num_tasks + 1):
        task_dir = f"courses/{name}/task_folder/task_{i}"
        os.makedirs(task_dir, exist_ok=True)
        
        # task.md
        with open(f"{task_dir}/task.md", "w") as f:
            f.write(f"# Task {i}\n\nWrite your task description here.")
        
        # example_solution.py
        with open(f"{task_dir}/example_solution.py", "w") as f:
            f.write("# Your solution here\n")
        
        # test file
        with open(f"{task_dir}/test_task_{i}.py", "w") as f:
            f.write('tests = {\n    "test_1": {\n        "input": "",\n        "expected_output": ""\n    }\n}\n')

# Usage
create_course("my_course", "My Course", 5)
```

---

## Next Steps

- Review [Models Documentation](models.md) for pedagogical model options
- Check [API Reference](api-reference.md) for programmatic course management
- See [Development Setup](development.md) for testing courses locally
