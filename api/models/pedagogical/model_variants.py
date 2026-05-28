"""Pedagogical model variants — consolidated from individual stub files.

Each variant is a thin configuration of Base_pedagogical_model that wires
together a task selector and a feedback module.  Keeping them in one place
makes the 2×2 matrix of {LLM, StateSpace} × {sequential, skipping} obvious.

State-space variants require optional dependencies and are imported
conditionally — check STATE_SPACE_AVAILABLE before using them.
"""

from models.pedagogical.base_pedagogical import Base_pedagogical_model
from models.pedagogical.content_selection.first_uncompleted_task import First_uncompleted_task_selector
from models.pedagogical.content_selection.skipping_easy_tasks import Skipping_task_selector
from models.pedagogical.feedback.llm_prototype_feedback_module import LLM_prototype_feedback_module
from models.knowledge_tracing.pfa_model import PFA_Model


# ── LLM-based variants ────────────────────────────────────────────────

class Prototype_pedagogical_model(Base_pedagogical_model):
    """Default LLM-powered model — both code + textual feedback, sequential tasks."""

    def __init__(self):
        self.task_selector = First_uncompleted_task_selector()
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="both")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}


class LLM_feedback_code_pedagogical_model(Base_pedagogical_model):
    """LLM feedback — code-only hints, sequential tasks."""

    def __init__(self):
        self.task_selector = First_uncompleted_task_selector()
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="code")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}


class LLM_feedback_textual_pedagogical_model(Base_pedagogical_model):
    """LLM feedback — text-only hints, sequential tasks."""

    def __init__(self):
        self.task_selector = First_uncompleted_task_selector()
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="textual")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}


class Skipping_tasks_pfa_pedagogical_model(Base_pedagogical_model):
    """LLM feedback with PFA-based task skipping."""

    def __init__(self):
        self.task_selector = Skipping_task_selector(PFA_Model)
        self.feedback_module = LLM_prototype_feedback_module()
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}


# ── Study 2025 group variants (LLM) ──────────────────────────────────

class Group_A_llm_base(Base_pedagogical_model):
    """Study 2025 Group A — LLM feedback, sequential tasks."""

    def __init__(self):
        self.task_selector = First_uncompleted_task_selector()
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="both")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}


class Group_C_llm_skipping(Base_pedagogical_model):
    """Study 2025 Group C — LLM feedback, PFA skipping."""

    def __init__(self):
        self.task_selector = Skipping_task_selector(PFA_Model)
        self.feedback_module = LLM_prototype_feedback_module(feedback_type="both")
        self.feedback_method = "LLM-next-step"
        self.task_summaries = {}


# ── State-space variants (optional dependencies) ─────────────────────

STATE_SPACE_AVAILABLE = False
STATE_SPACE_IMPORT_ERROR = None

try:
    from models.pedagogical.feedback.state_space_feedback_module import State_space_feedback_module

    class State_space_feedback_pedagogical_model(Base_pedagogical_model):
        """State-space-based feedback, sequential tasks."""

        def __init__(self):
            self.task_selector = First_uncompleted_task_selector()
            self.feedback_module = State_space_feedback_module()
            self.feedback_method = "State-space-based"

    class Simple_state_space_feedback_pedagogical_model(Base_pedagogical_model):
        """State-space feedback without persistent state."""

        def __init__(self):
            self.task_selector = First_uncompleted_task_selector()
            self.feedback_module = State_space_feedback_module(persistent_state_space=False)
            self.feedback_method = "Simple-state-space-based"

    class Group_B_state_space_base(Base_pedagogical_model):
        """Study 2025 Group B — state-space feedback, sequential tasks."""

        def __init__(self):
            self.task_selector = First_uncompleted_task_selector()
            self.feedback_module = State_space_feedback_module(
                selector="embedding", persistent_state_space="true"
            )
            self.feedback_method = "State-space-based"
            self.task_summaries = {}

    class Group_D_state_space_skipping(Base_pedagogical_model):
        """Study 2025 Group D — state-space feedback, PFA skipping."""

        def __init__(self):
            self.task_selector = Skipping_task_selector(PFA_Model)
            self.feedback_module = State_space_feedback_module(
                selector="embedding", persistent_state_space="true"
            )
            self.feedback_method = "State-space-based"
            self.task_summaries = {}

    STATE_SPACE_AVAILABLE = True

except ModuleNotFoundError as exc:
    STATE_SPACE_IMPORT_ERROR = exc
    State_space_feedback_pedagogical_model = None
    Simple_state_space_feedback_pedagogical_model = None
    Group_B_state_space_base = None
    Group_D_state_space_skipping = None
