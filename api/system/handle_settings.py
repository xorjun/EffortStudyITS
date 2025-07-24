from fastapi import APIRouter, Depends, HTTPException, status
import os
from db import database
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from system.schemas import AppSettings

router = APIRouter()

@router.post("/update")
async def update_settings(settings: AppSettings, user: User = Depends(current_active_verified_user)):
    if (not "admin" in user.roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )
    else:
        await database.update_settings(vars(settings))
        return {"response": "Settings updated"}
    

@router.get("/get")
async def get_settings(user: User = Depends(current_active_verified_user)) -> AppSettings:
    if (not "admin" in user.roles):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to access this resource"
        )
    else:
        settings = await database.get_settings()
        return settings