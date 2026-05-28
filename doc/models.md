# Models Documentation

## Overview

SCRIPT uses a modular model architecture that separates concerns into three main categories:
1. **Pedagogical Models**: Control feedback generation and task selection strategies
2. **Knowledge Tracing Models**: Track learner competency and predict performance
3. **Domain Models**: Provide domain-specific feedback and validation

---

## Pedagogical Models

Pedagogical models define the overall tutoring strategy, combining task selection algorithms and feedback mechanisms.

### Base Pedagogical Model

**Location**: `api/models/pedagogical/base_pedagogical.py`

All pedagogical models inherit from `Base_pedagogical_model`:

```python
class Base_pedagogical_model():
    task_selector: Base_task_selector
    feedback_generator: Base_feedback_generator
```

### Available Pedagogical Models

#### 1. Prototype Model (`prototype`)

**Class**: `Prototype_pedagogical_model`

Basic model for testing and demonstration.

**Features:**
- Simple sequential task selection
- No adaptive behavior
- Basic feedback generation

**Use Case:** Testing, debugging, baseline comparison

---

#### 2. Skipping Tasks with PFA (`skipping_pfa`)

**Class**: `Skipping_tasks_pfa_pedagogical_model`

**Default model** for SCRIPT. Combines adaptive task selection with PFA-based knowledge tracing.

**Features:**
- **Task Selection**: Adaptive selection based on learner competency
- **Knowledge Tracing**: PFA (Performance Factor Analysis)
- **Skipping**: Allows skipping tasks below competency threshold
- **Feedback**: Basic feedback on test results

**How it works:**
1. PFA model predicts success probability for each task
2. Tasks with very high probability (> 0.85) are skipped
3. Tasks with moderate probability (0.3-0.85) are recommended
4. Mandatory tasks are never skipped

**Configuration:**
```json
{
  "pedagogical_model": "skipping_pfa",
  "skip_threshold": 0.85,
  "min_difficulty": 0.3
}
```

---

#### 3. LLM Textual Feedback (`prototype_textual_feedback`)

**Class**: `LLM_feedback_textual_pedagogical_model`

Provides natural language feedback using LLM.

**Features:**
- Textual explanations of errors
- Conceptual hints
- No code-specific feedback

**Prompt Template:**
```
You are a programming tutor. The student is working on: {task_description}
Their code: {student_code}
Test results: {test_results}
Provide helpful feedback without giving away the solution.
```

---

#### 4. LLM Code Feedback (`prototype_code_feedback`)

**Class**: `LLM_feedback_code_pedagogical_model`

Provides code-specific feedback using LLM.

**Features:**
- Code suggestions
- Syntax error explanations
- Best practices recommendations

**Prompt Template:**
```
Analyze this Python code and provide specific feedback:
{student_code}

Expected output: {expected_output}
Actual output: {actual_output}
```

---

#### 5. State-Space Feedback (`state-space`)

**Class**: `State_space_feedback_pedagogical_model`

Uses pre-computed expert solution paths for feedback.

**Features:**
- Matches student code against expert states
- Provides step-by-step guidance
- Works offline (no LLM required)
- Highly accurate for well-defined tasks

**How it works:**
1. Expert solutions pre-computed as state spaces
2. Student code converted to state representation
3. Nearest expert state found using embedding similarity
4. Feedback guides student toward nearest valid state

**State Space Structure:**
```python
{
  "states": [
    {
      "state": "code_string",
      "state_embedding": [0.1, 0.2, ...],
      "hashed_state": "hash"
    }
  ],
  "adj_matrix": [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
}
```

---

#### 6. Simple State-Space Feedback (`simple-state-space`)

**Class**: `Simple_state_space_feedback_pedagogical_model`

Simplified version of state-space feedback.

**Features:**
- Direct string matching (no embeddings)
- Faster but less flexible
- Good for exact match scenarios

---

### Research Group Models (Study 2025)

Special pedagogical models for research studies:

#### Group A: LLM Base (`group_A`)
- Standard LLM feedback
- No adaptive task selection
- Control group configuration

#### Group B: State-Space Base (`group_B`)
- State-space feedback
- No adaptive task selection

#### Group C: LLM + Skipping (`group_C`)
- LLM feedback
- PFA-based task skipping

#### Group D: State-Space + Skipping (`group_D`)
- State-space feedback
- PFA-based task skipping

---

## Knowledge Tracing Models

Track learner knowledge and predict performance on future tasks.

### PFA Model (Performance Factor Analysis)

**Location**: `api/models/knowledge_tracing/pfa_model.py`

**Class**: `PFA_Model`

#### Overview

PFA models learner competency as a function of:
- **Skills**: Discrete competencies (e.g., "loops", "conditionals")
- **Success Rate**: Count of successful attempts per skill
- **Failure Rate**: Count of failed attempts per skill

#### Mathematical Model

Probability of success on task $t$:

$$P(\text{success}|t) = \frac{1}{1 + e^{-\text{logit}}}$$

Where:

$$\text{logit} = \sum_{i=1}^{n_{\text{skills}}} q_{ti} \cdot (w_{i,s} \cdot s_i + w_{i,f} \cdot f_i + w_{i,b})$$

- $q_{ti}$: Q-matrix entry (does task $t$ require skill $i$?)
- $w_{i,s}$: Weight for success rate of skill $i$
- $w_{i,f}$: Weight for failure rate of skill $i$
- $w_{i,b}$: Bias term for skill $i$
- $s_i$: Student's success count for skill $i$
- $f_i$: Student's failure count for skill $i$

#### Q-Matrix

Maps tasks to required skills:

```json
{
  "task_print_hello": [1, 0, 0, 0],  // Requires skill 0 only
  "task_for_loop": [0, 1, 1, 0],     // Requires skills 1 and 2
  "task_conditionals": [0, 0, 1, 1]  // Requires skills 2 and 3
}
```

#### Skill Weights

Learned via logistic regression:

```json
{
  "skill_weights_pfa": [
    0.5,  // skill_0 success weight
    -0.3, // skill_0 failure weight
    -1.0, // skill_0 bias
    0.6,  // skill_1 success weight
    -0.4, // skill_1 failure weight
    -0.8, // skill_1 bias
    ...
  ]
}
```

#### Weight Update

Weights are updated periodically (via APScheduler) using logistic regression on all learner data:

```python
from sklearn.linear_model import LogisticRegression

# Build feature matrix X and target vector Y
# X: [success_counts, failure_counts, skill_indicators]
# Y: [task_success_binary]

model = LogisticRegression(penalty='l2', C=1.0, fit_intercept=False)
model.fit(X, Y)

new_weights = -model.coef_[0]  # Negative for logit formulation
```

#### Usage Example

```python
pfa = PFA_Model(n_parameters=3)
await pfa.set_user(user, course)

# Predict success probability
prob = pfa.completion_probability("task_for_loop")
print(f"Success probability: {prob:.2%}")

# Update weights (admin only)
await pfa.update_course_weights(course)
```

---

## Task Selection Models

Determine which task to present to the learner next.

### Base Task Selector

**Location**: `api/models/pedagogical/content_selection/base.py`

**Interface:**
```python
class Base_task_selector(ABC):
    @abstractmethod
    async def select(self, user: User, topic: str = None):
        raise NotImplementedError
```

### Skipping Task Selector

**Class**: `Skipping_task_selector`

**Algorithm:**

```python
async def select(self, user, topic=None):
    # 1. Get curriculum
    tasks = get_curriculum(course)
    
    # 2. Filter by topic (if specified)
    if topic:
        tasks = filter_by_topic(tasks, topic)
    
    # 3. Remove completed tasks
    tasks = [t for t in tasks if t not in user.completed_tasks]
    
    # 4. Compute probabilities
    probs = {t: pfa.completion_probability(t) for t in tasks}
    
    # 5. Select task in target range
    target_tasks = {t: p for t, p in probs.items() 
                    if 0.3 <= p <= 0.85}
    
    if target_tasks:
        # Return task closest to 0.5 (optimal challenge)
        return min(target_tasks, key=lambda t: abs(probs[t] - 0.5))
    
    # 6. Fallback: return lowest probability task
    return min(probs, key=probs.get)
```

**Parameters:**
- `skip_threshold`: Don't present tasks with p > threshold (default: 0.85)
- `min_difficulty`: Don't present tasks with p < threshold (default: 0.3)
- `target_probability`: Ideal probability for optimal challenge (default: 0.5)

---

## Feedback Generators

Generate feedback for learner submissions.

### LLM Feedback Generator

**Location**: `api/models/domain/feedback.py`

**Process:**
1. Construct prompt with task description, student code, and test results
2. Send to LLM API (Ollama or OpenAI)
3. Parse response
4. Store feedback in database

**Example Prompt:**
```
System: You are an expert programming tutor providing feedback to students.

User: The student is working on this task:
{task_description}

Their code:
{student_code}

Test results:
{test_results}

Provide constructive feedback that helps them improve without giving away the solution.
```

### State-Space Feedback Generator

**Process:**
1. Compute embedding of student code
2. Find nearest state in expert state space
3. Compute distance to nearest state
4. Generate hint based on difference

**Example:**
```python
student_code = "print('Hello')"
expert_state = "print('Hello, World!')"

# Compute similarity
similarity = cosine_similarity(
    embed(student_code),
    embed(expert_state)
)

if similarity > 0.9:
    feedback = "You're very close! Check your output carefully."
elif similarity > 0.7:
    feedback = "You're on the right track. Consider what the output should be."
else:
    feedback = "Your approach is different from expected. Review the task description."
```

---

## Model Manager

**Location**: `api/models/model_manager.py`

**Class**: `Model_Manager`

Central registry for all models. Provides model selection and instantiation.

### Usage

```python
from models.model_manager import model_manager

# Get pedagogical model by name
model = model_manager.get_pedagogical_model("skipping_pfa")

# Get model for specific user
model = await model_manager.get_pedagogical_model_by_user(user)

# Validate course for model
status, error = model_manager.validate_course(course)

# Update course weights
await model_manager.update_course_weights(course)
```

### Registered Models

```python
pedagogical_models = {
    "prototype": Prototype_pedagogical_model(),
    "skipping_pfa": Skipping_tasks_pfa_pedagogical_model(),
    "prototype_textual_feedback": LLM_feedback_textual_pedagogical_model(),
    "prototype_code_feedback": LLM_feedback_code_pedagogical_model(),
    "state-space": State_space_feedback_pedagogical_model(),
    "simple-state-space": Simple_state_space_feedback_pedagogical_model(),
    "group_A": Group_A_llm_base(),
    "group_B": Group_B_state_space_base(),
    "group_C": Group_C_llm_skipping(),
    "group_D": Group_D_state_space_skipping(),
}
```

---

## Creating Custom Models

### Custom Pedagogical Model

```python
from models.pedagogical.base_pedagogical import Base_pedagogical_model
from models.pedagogical.content_selection.base import Base_task_selector

class My_Custom_Selector(Base_task_selector):
    async def select(self, user, topic=None):
        # Your selection logic
        return selected_task

class My_Custom_Pedagogical_Model(Base_pedagogical_model):
    def __init__(self):
        self.task_selector = My_Custom_Selector()
        self.feedback_generator = None  # Or custom generator
```

### Register Custom Model

```python
# In model_manager.py __init__
self.pedagogical_models["my_custom"] = My_Custom_Pedagogical_Model()
```

### Use Custom Model

```json
{
  "course_settings_list": [
    {
      "pedagogical_model": "my_custom"
    }
  ]
}
```

---

## Model Evaluation

### Metrics

1. **Task Success Rate**: % of tasks completed successfully
2. **Time to Completion**: Average time per task
3. **Learning Gain**: Pre-test to post-test improvement
4. **Engagement**: Number of feedback requests, attempts
5. **Prediction Accuracy**: PFA model calibration

### Evaluation Scripts

```python
# Compute PFA accuracy
from sklearn.metrics import roc_auc_score

predictions = []
actuals = []

for enrollment in enrollments:
    for task in enrollment.tasks_attempted:
        prob = pfa.completion_probability(task)
        actual = 1 if task in enrollment.tasks_completed else 0
        predictions.append(prob)
        actuals.append(actual)

auc = roc_auc_score(actuals, predictions)
print(f"PFA AUC: {auc:.3f}")
```

---

## Background Tasks

### Skill Weight Updates

PFA skill weights are updated periodically using APScheduler:

**Location**: `api/main.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    update_skill_parameters,
    trigger=IntervalTrigger(hours=24),
    id='update_pfa_weights'
)
scheduler.start()
```

**Update Function**: `api/models/domain/skill_weights_pfa_update.py`

```python
async def update_skill_parameters():
    courses = await database.get_courses()
    for course in courses:
        if course.domain != "Surveys":
            await pfa_model.update_course_weights(course)
```

---

## Best Practices

1. **Model Selection**: Choose based on research goals
   - Use `skipping_pfa` for adaptive tutoring
   - Use `state-space` for structured domains
   - Use `prototype` for debugging

2. **PFA Configuration**:
   - Ensure Q-matrix matches curriculum
   - Validate course before use
   - Update weights regularly (daily)

3. **State-Space Feedback**:
   - Pre-compute state spaces for all tasks
   - Use embeddings for flexible matching
   - Keep state spaces up-to-date

4. **LLM Feedback**:
   - Monitor API costs
   - Implement rate limiting
   - Cache common feedback

5. **Testing**:
   - Validate models on hold-out data
   - A/B test new models
   - Monitor prediction accuracy

---

## References

- **PFA**: Pavlik Jr, P. I., Cen, H., & Koedinger, K. R. (2009). Performance Factors Analysis–A New Alternative to Knowledge Tracing.
- **ITS**: VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems.
- **State-Space**: Anderson, J. R., et al. (1995). Cognitive tutors: Lessons learned.
