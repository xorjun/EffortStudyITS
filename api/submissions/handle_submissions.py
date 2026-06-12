import traceback
from fastapi import APIRouter, Depends, HTTPException
from courses.schemas import TaskType
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from submissions.schemas import Base_Submission
from models.domain.submissions.submissions import handle_submission, mark_task_completed

from db import database
from sys import __stdout__
import ast as _ast

router = APIRouter()

@router.post("/submit")
async def submit(submission: Base_Submission, user: User = Depends(current_active_verified_user)):
    try:
        return await handle_submission(submission, user)
    except Exception as e:
        print(traceback.format_exc())
        return {"status": 500, "message": f"{type(e)}: {str(e)}"}

@router.get("/submission/feedback/{submission_id}")
async def send_feedback(submission_id):
    feedback = await database.get_submission(str(submission_id))
    return feedback

@router.get("/submission/summary/{submission_id}")
async def submission_summary(submission_id: str, user: User = Depends(current_active_verified_user)):
    """Return a plain-English summary of what the user's submitted code
    achieves. Used by the feedback panel to show "what the code was able
    to achieve" right after the learner submits.

    The summary is two parts:
    - A deterministic static-analysis summary derived from the Python AST
      (always returned, cheap, no LLM dependency).
    - When the platform has an LLM configured, a one-line natural-language
      summary produced via the existing language generation service. This
      enrichment is best-effort — if the LLM call fails or times out, the
      static summary is still returned.
    """
    try:
        submission = await database.get_submission(str(submission_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # The submission doc has a `code` attribute on tested submissions.
    code = getattr(submission, "code", None) or ""
    static_summary = _summarize_python_code(code)

    # Best-effort LLM enrichment. We never block the response on this.
    llm_summary: str | None = None
    try:
        from services.language_generation import (
            generate_language,
            has_language_generation_configuration,
        )
        if await has_language_generation_configuration():
            prompt = (
                "In one or two short sentences, describe in plain English what "
                "the following Python code does. Mention the function or top-level "
                "behavior, the inputs and outputs, and any side effects. Do not "
                "judge correctness.\n\n"
                f"```python\n{code}\n```\n\nSummary:"
            )
            llm_summary = await generate_language(prompt, model=None)
            llm_summary = (llm_summary or "").strip() or None
    except Exception:  # pragma: no cover - best-effort enrichment
        llm_summary = None

    return {
        "submission_id": str(submission_id),
        "static_summary": static_summary,
        "llm_summary": llm_summary,
    }

# ── helpers ────────────────────────────────────────────────────────────


def _summarize_python_code(code: str) -> str:
    """Produce a deterministic, plain-English description of a Python
    snippet by inspecting its AST. Designed to be terse (one short
    paragraph) and never to throw on weird input.
    """
    if not code or not code.strip():
        return "Your submission was empty — there is no code to evaluate."

    try:
        tree = _ast.parse(code)
    except SyntaxError as exc:
        return (
            f"Your code could not be parsed as valid Python (line "
            f"{exc.lineno}: {exc.msg or 'syntax error'}). The most likely "
            "cause is a missing colon, an unmatched bracket, or a typo in a "
            "keyword."
        )
    except Exception as exc:  # pragma: no cover - defensive
        return f"Your code could not be analyzed: {type(exc).__name__}."

    function_names: list[str] = []
    class_names: list[str] = []
    print_literals: list[str] = []
    has_return = False
    has_loop = False
    has_if = False
    has_assignment = False
    has_import = False

    for node in tree.body:
        if isinstance(node, _ast.FunctionDef):
            function_names.append(node.name)
            for sub in _ast.walk(node):
                if isinstance(sub, _ast.Return) and sub.value is not None:
                    has_return = True
                if isinstance(sub, _ast.Call) and isinstance(sub.func, _ast.Name) and sub.func.id == "print":
                    args = [_ast.unparse(a) for a in sub.args]
                    print_literals.append(", ".join(args) if args else "(no arguments)")
        elif isinstance(node, _ast.ClassDef):
            class_names.append(node.name)
        elif isinstance(node, (_ast.Import, _ast.ImportFrom)):
            has_import = True
        elif isinstance(node, _ast.Assign):
            has_assignment = True
        elif isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Call):
            if isinstance(node.value.func, _ast.Name) and node.value.func.id == "print":
                args = [_ast.unparse(a) for a in node.value.args]
                print_literals.append(", ".join(args) if args else "(no arguments)")
        elif isinstance(node, _ast.If):
            has_if = True
        elif isinstance(node, (_ast.For, _ast.While)):
            has_loop = True
            # Surface print() calls inside loops so a learner who prints
            # inside a loop sees it in the summary.
            for sub in _ast.walk(node):
                if isinstance(sub, _ast.Call) and isinstance(sub.func, _ast.Name) and sub.func.id == "print":
                    args = [_ast.unparse(a) for a in sub.args]
                    print_literals.append(", ".join(args) if args else "(no arguments)")

    if not tree.body:
        return "Your code is empty (only comments or whitespace)."

    if not function_names and not class_names and not print_literals and not has_loop and not has_if and not has_assignment and not has_import:
        return "Your code parses as valid Python but does not contain any top-level statements or functions."

    # Compose the human-readable summary.
    sentence_parts: list[str] = []
    if has_import:
        sentence_parts.append("Your code imports one or more modules")
    if class_names:
        joined = ", ".join(f"`{n}`" for n in class_names)
        sentence_parts.append(f"defines the class{'es' if len(class_names) != 1 else ''} {joined}")
    if function_names:
        joined = ", ".join(f"`{n}`" for n in function_names)
        sentence_parts.append(f"defines the function{'s' if len(function_names) != 1 else ''} {joined}")
    if has_assignment:
        sentence_parts.append("creates top-level variables")
    if print_literals:
        sample = print_literals[:3]
        joined = "; ".join(f"`print({a})`" for a in sample)
        if len(print_literals) > 3:
            joined += f"; and {len(print_literals) - 3} more"
        sentence_parts.append(f"prints {joined}")
    if has_return:
        sentence_parts.append("returns a value from the function")
    if has_loop:
        sentence_parts.append("uses a loop")
    if has_if:
        sentence_parts.append("branches on a condition")
    if not sentence_parts:
        sentence_parts.append("Your code parses as valid Python")

    summary = ", ".join(sentence_parts) + "."
    return summary


# Temporary
@router.post("/mark_solved/{task_unique_name}")
async def mark_solved(task_unique_name: str, user: User = Depends(current_active_verified_user)):
    # only allow plot functions to be marked as solved via this
    task = await database.get_task(task_unique_name)
    if task.type in [TaskType.PlotFunction]:
        return await mark_task_completed(task_unique_name, user)
    else:
        return {"status": 403, "message": "Marking as solved is only allowed to task type 'PlotFunctuon'."}