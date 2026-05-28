from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.study_metrics import collect_study_metrics, _metrics_cache_invalidate
from db import database
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from system.schemas import AppSettings, EditorPolicy, StudyMetricsResponse
from users.schemas import UserLevel
from datetime import datetime

router = APIRouter()


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
    settings = await database.get_settings()
    return EditorPolicy(disable_editor_copy_paste=settings.disable_editor_copy_paste)