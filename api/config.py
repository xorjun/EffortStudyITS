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
            self.database_pwd = os.environ.get("DB_SERVICE_PW", "")
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
            self.database_pwd = os.environ.get("DB_SERVICE_PW", "")
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
            self.database_pwd = os.environ.get("DB_SERVICE_PW", "")
            self.database_host = "mongodb"
            self.database_port = 27017
            self.judge0_mode = os.environ.get("JUDGE0_MODE")

        elif self.env == "standalone":
            # Single-image deployment: all config via env vars
            dotenv.load_dotenv(dotenv.find_dotenv())
            self.database_pwd = os.environ.get("DB_SERVICE_PW", "")
            self.database_host = os.environ.get("DATABASE_HOST", "mongodb")
            self.database_port = int(os.environ.get("DATABASE_PORT", "27017"))
            self.database_usr = os.environ.get("DATABASE_USER", "backend_service_user")
            self.judge0_mode = os.environ.get("JUDGE0_MODE", "none")
            if self.judge0_mode == "local":
                self.judge0_host = os.environ.get("JUDGE0_URL", "http://j0-server:2358")
                self.judge0_token = os.environ.get("JUDGE0_TOKEN", None)
            elif self.judge0_mode == "remote":
                self.judge0_host = os.environ.get("JUDGE0_URL")
                self.judge0_token = os.environ.get("JUDGE0_TOKEN")
            elif self.judge0_mode == "none":
                self.judge0_host = None
                self.judge0_token = None
            else:
                raise Exception("Judge0 mode not specified correctly")


        else:
            raise ValueError("Invalid 'env' value. Supported values are 'development', 'development-docker', 'standalone', 'production', and 'staging'.")

        fallback_default = "true" if self.env in ["development", "development-docker"] and self.judge0_mode == "local" else "false"
        self.unsafe_local_execution_fallback_enabled = os.environ.get("UNSAFE_LOCAL_EXECUTION_FALLBACK", fallback_default).strip().lower() == "true"
        
        #TODO Eventually this should be an Admin setting
        if self.env in ["development", "development-docker"]:
            self.email_enabled = False
        else: 
            self.email_enabled = True

        self.llm_api_type = os.environ.get("LLM_API_TYPE", "").strip().lower()
        self.llm_api_url = os.environ.get("LLM_API_URL", "").strip()
        self.llm_api_key = os.environ.get("LLM_API_KEY", "").strip()
        self.llm_default_model = os.environ.get("LLM_DEFAULT_MODEL", "").strip()

        mistral_api_key = os.environ.get("MISTRAL_API_KEY", "").strip()
        mistral_api_url = os.environ.get("MISTRAL_API_URL", "").strip() or "https://api.mistral.ai/v1/"
        mistral_default_model = os.environ.get("MISTRAL_MODEL", "").strip() or "mistral-small-latest"

        if not self.llm_api_type and mistral_api_key:
            self.llm_api_type = "mistral"

        if self.llm_api_type == "mistral":
            self.llm_api_url = self.llm_api_url or mistral_api_url
            self.llm_api_key = self.llm_api_key or mistral_api_key
            self.llm_default_model = self.llm_default_model or mistral_default_model
        elif self.llm_api_type == "open-ai":
            self.llm_api_url = self.llm_api_url or (os.environ.get("OPENAI_API_URL", "").strip() or "https://api.openai.com/v1/")
            self.llm_api_key = self.llm_api_key or os.environ.get("OPENAI_API_KEY", "").strip()
            self.llm_default_model = self.llm_default_model or (os.environ.get("OPENAI_MODEL", "").strip() or "gpt-4o-mini")
        else:
            self.llm_default_model = self.llm_default_model or (os.environ.get("OLLAMA_MODEL", "").strip() or "qwen3-coder:30b")

config = Config()
