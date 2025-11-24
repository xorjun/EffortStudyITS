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
            self.judge0_mode = os.environ.get("JUDGE0_MODE")
            if self.judge0_mode == "local":
                self.judge0_host = "http://localhost:2358"
                self.judge0_token = None
            elif self.judge0_mode == "remote":
                self.judge0_host = os.environ.get("JUDGE0_URL")
                self.judge0_token = os.environ.get("JUDGE0_TOKEN")
            else: 
                raise Exception("Judge0 mode not specified correctly")

        elif self.env == "development-docker":
            self.database_pwd = os.environ.get("DB_SERVICE_PW")
            self.database_host = "mongodb"
            self.database_port = 27017
            self.judge0_mode = os.environ.get("JUDGE0_MODE")
            if self.judge0_mode == "local":
                self.judge0_host = "http://j0-server:2358"
                self.judge0_token = None
            elif self.judge0_mode == "remote":
                self.judge0_host = os.environ.get("JUDGE0_URL")
                self.judge0_token = os.environ.get("JUDGE0_TOKEN")
            else: 
                raise Exception("Judge0 mode not specified correctly")

        elif self.env == "production":
            self.database_pwd = os.environ.get("DB_SERVICE_PW")
            self.database_host = "mongodb"
            self.database_port = 27017
            self.judge0_mode = os.environ.get("JUDGE0_MODE")
            if self.judge0_mode == "local":
                self.judge0_host = "http://j0-server:2358"
                self.judge0_token = None
            elif self.judge0_mode == "remote":
                self.judge0_host = os.environ.get("JUDGE0_URL")
                self.judge0_token = os.environ.get("JUDGE0_TOKEN")
            else: 
                raise Exception("Judge0 mode not specified correctly")


        else:
            raise ValueError("Invalid 'env' value. Supported values are 'development', 'production', and 'staging'.")
        
        #TODO Eventually this should be an Admin setting
        if self.env in ["development", "development-docker"]:
            self.email_enabled = False
        else: 
            self.email_enabled = True

config = Config()
