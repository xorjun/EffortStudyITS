import os
import dotenv
class Config:
    """Configuration for different environments for the api to run in.
    """
    def __init__(self):
        self.load_config()

    def load_config(self):
        # Get the value of the "env" environment variable, defaulting to "development"
        self.env = os.environ.get("ITS_ENV", "development")
        
        self.database_usr = "backend_service_user"

        if self.env == "development":
            dotenv.load_dotenv(dotenv.find_dotenv())
            self.database_pwd = os.environ.get("DB_SERVICE_PW")
            self.database_host = "localhost"
            self.database_port = 27017
            self.judge0_host = "localhost"

        elif self.env == "development-docker":
            self.database_pwd = os.environ.get("DB_SERVICE_PW")
            self.database_host = "mongodb"
            self.database_port = 27017
            self.judge0_host = "j0-server"

        elif self.env == "production":
            self.database_pwd = os.environ.get("DB_SERVICE_PW")
            self.database_host = "mongodb"
            self.database_port = 27017
            self.judge0_host = "j0-server"


        else:
            raise ValueError("Invalid 'env' value. Supported values are 'development', 'production', and 'staging'.")
        
        #TODO Eventually this should be an Admin setting
        if self.env in ["development", "development-docker"]:
            self.email_enabled = False
        else: 
            self.email_enabled = True

config = Config()
