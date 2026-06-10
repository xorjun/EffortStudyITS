"""Regression tests for feedback submission schema defaults.

Background: the /api/settings/study_metrics endpoint does a
Evaluated_feedback_submission.find().to_list() over the whole
Submission collection, which re-validates every MongoDB doc against the
Pydantic model. Legacy documents written before `feedback_method` and
`feedback` were added to the schema would previously fail validation and
crash the whole endpoint with a 500.

The fix makes both fields default to "" so legacy docs validate cleanly.
We assert the defaults at the Pydantic class level — that's the contract
the fix establishes, and it doesn't require a running MongoDB.
"""
from feedback.schemas import Evaluated_feedback_submission


def test_feedback_method_defaults_to_empty_string():
    """Legacy docs without feedback_method must validate as ""."""
    assert Evaluated_feedback_submission.model_fields["feedback_method"].default == ""


def test_feedback_defaults_to_empty_string():
    """Legacy docs without feedback must validate as ""."""
    assert Evaluated_feedback_submission.model_fields["feedback"].default == ""
