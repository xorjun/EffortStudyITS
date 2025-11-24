from fastapi import APIRouter, Depends
from users.handle_users import current_active_verified_user
from db.db_connector_beanie import User
from surveys.schemas import Survey
from db import database

router = APIRouter()


@router.post("/submit")
async def submit_survey(survey: Survey, user: User = Depends(current_active_verified_user)):
    if user.settings["dataCollection"] == True:
        prev_survey = await database.get_survey(survey.corresponding_id, survey.corresponding_id_type)
        if prev_survey is None:
            await database.create_survey(survey)
        else: 
            prev_survey.survey_results = survey.survey_results
            await database.update_survey(prev_survey)


