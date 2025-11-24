from beanie import PydanticObjectId
from beanie import Document
from typing import Optional

class Survey(Document):

    corresponding_id: str
    corresponding_id_type: str
    survey_results: dict