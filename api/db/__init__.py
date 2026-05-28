from db.db_connector_beanie import database
from config import config


database = database(
    database_host=config.database_host,
    database_user=config.database_usr,
    database_pwd=config.database_pwd,
)
