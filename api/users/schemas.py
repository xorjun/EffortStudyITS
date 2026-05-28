from enum import Enum
import functools
from beanie import PydanticObjectId
from fastapi_users import schemas
from typing import Optional
from beanie import Document
from fastapi_users_db_beanie import BeanieBaseUserDocument
from pydantic import ConfigDict
from pymongo import IndexModel
from pymongo.collation import Collation


@functools.total_ordering
class UserLevel(Enum):
    # Warning: The level of access gets determined by the order of these enums.
    admin = "admin"
    tutor = "tutor"
    student = "student"

    # These functions make the UserLevel comparable, so eg. UserLevel.student < UserLevel.admin will eval to true
    # Higher on the list means higher in rank!
    def __eq__(self, other) -> bool:
        try:
            return (
                self._member_names_.index(self.name) ==
                self._member_names_.index(UserLevel(other).name)
            )
        except:
            raise ValueError(f"Comparison between '{self.__class__}' and '{other}' of class {self.__class__} not possible!")

    def __gt__(self, other) -> bool:
        try:
            return (
                self._member_names_.index(self.name) <
                self._member_names_.index(UserLevel(other).name)
            )
        except:
            raise ValueError(f"Comparison between '{self.__class__}' and '{other}' of class {self.__class__} not possible!")


class User(BeanieBaseUserDocument):
    email: str
    username: str
    verification_email: Optional[str] = None
    encrypted_email: Optional[str] = None
    current_course: str
    enrolled_courses: list
    register_datetime: dict
    settings: dict
    roles: list[UserLevel]

    class Settings:
        """Here we are overwriting the settings class from BeanieBaseUser in order to allow for the optional roles field.
        Basically this allows us to exclude roles from the UserCreate schema in order to avoid security breaches.
        """

        keep_nulls = False
        email_collation = Collation("en", strength=2)
        indexes = [
            IndexModel("email", unique=True),
            IndexModel(
                "email", name="case_insensitive_email_index", collation=email_collation
            ),
        ]

    model_config = ConfigDict(use_enum_values=True)


class UserRead(schemas.BaseUser[PydanticObjectId]):
    email: str
    username: str
    current_course: str
    enrolled_courses: list
    register_datetime: dict
    settings: dict
    roles: Optional[list[UserLevel]] = None
    pass


class UserCreate(schemas.BaseUserCreate):
    email: str
    verification_email: str
    username: str
    current_course: str
    enrolled_courses: list
    register_datetime: dict
    settings: dict
    roles: Optional[list[UserLevel]] = None
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """This Schema defines how the request body for the user-patch enpoints has to look.
    Every setting that is modifyable through the profile-page should be part of this schema.
    Other user-fields, that get update during interactions with the system automatically,
    are directly updated through database calls. This might be an anti-pattern and change
    in later iterations. Potentially all such information should be stored in different
    documents.
    """

    username: str
    register_datetime: dict
    settings: dict
    current_course: str
    pass


class GlobalAccountList(Document):
    hashed_email_list: list
