import time
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.study_metrics import collect_study_metrics, _metrics_cache_invalidate
from db import database
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from system.schemas import AppSettings, EditorPolicy, StudyMetricsResponse
from users.schemas import UserLevel
from datetime import datetime

router = APIRouter()


# ── Editor policy cache ──────────────────────────────────────────────
# The /editor_policy endpoint is hit on every new task fetch by every
# participant. The value changes only via the admin panel (rarely) so
# a 60s cache is invisible to learners and cuts one MongoDB round-trip
# per task transition.
_EDITOR_POLICY_CACHE: dict = {"response": None, "timestamp": 0.0, "ttl": 60.0}


def _editor_policy_cache_get() -> EditorPolicy | None:
    if _EDITOR_POLICY_CACHE["response"] is not None:
        if time.monotonic() - _EDITOR_POLICY_CACHE["timestamp"] < _EDITOR_POLICY_CACHE["ttl"]:
            return _EDITOR_POLICY_CACHE["response"]
    return None


def _editor_policy_cache_set(response: EditorPolicy) -> None:
    _EDITOR_POLICY_CACHE["response"] = response
    _EDITOR_POLICY_CACHE["timestamp"] = time.monotonic()


def _editor_policy_cache_invalidate() -> None:
    _EDITOR_POLICY_CACHE["response"] = None
    _EDITOR_POLICY_CACHE["timestamp"] = 0.0


def _require_admin(user: User) -> None:
    if max([UserLevel(role) for role in user.roles]) < UserLevel.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )

@router.post("/update")
async def update_settings(settings: AppSettings, user: User = Depends(current_active_verified_user)):
    _require_admin(user)
    await database.update_settings(settings.model_dump(exclude={"id"}))
    # The /editor_policy endpoint is cached; any setting change can flip
    # the policy. Invalidate eagerly so the next learner request sees
    # the new value without waiting for the TTL to elapse.
    _editor_policy_cache_invalidate()
    return {"response": "Settings updated"}
    

@router.get("/get")
async def get_settings(user: User = Depends(current_active_verified_user)) -> AppSettings:
    _require_admin(user)
    settings = await database.get_settings()
    return settings


@router.get("/study_metrics")
async def get_study_metrics(
    user: User = Depends(current_active_verified_user),
    from_date: str | None = Query(None, description="Filter from date (ISO format, e.g. 2026-05-01)"),
    to_date: str | None = Query(None, description="Filter to date (ISO format, e.g. 2026-05-28)"),
    force: bool = Query(False, description="Bypass cache and compute fresh metrics"),
) -> StudyMetricsResponse:
    _require_admin(user)
    from_dt = datetime.fromisoformat(from_date) if from_date else None
    to_dt = datetime.fromisoformat(to_date) if to_date else None
    if force:
        _metrics_cache_invalidate()
    return await collect_study_metrics(from_date=from_dt, to_date=to_dt, force_refresh=force)


@router.get("/editor_policy")
async def get_editor_policy() -> EditorPolicy:
    cached = _editor_policy_cache_get()
    if cached is not None:
        return cached
    settings = await database.get_settings()
    response = EditorPolicy(disable_editor_copy_paste=settings.disable_editor_copy_paste)
    _editor_policy_cache_set(response)
    return response