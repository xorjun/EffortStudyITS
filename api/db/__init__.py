from db.db_connector_beanie import database
#from db.db_connector_beanie import db as database_beanie
from db.db_connector_beanie import User
from db.db_connector_beanie import get_user_db
from config import config

database = database(database_host=config.database_host, 
                    database_user=config.database_usr,
                    database_pwd=config.database_pwd)