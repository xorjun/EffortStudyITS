import asyncio
import threading
import time
from transformers import AutoModel, AutoTokenizer
import os
from config import config

class EmbeddingModelManager:
    """Singelton class to cache the embedding model in order to save execution time and free RAM if necessary."""
    _instance = None
    _lock = asyncio.Lock()  # Use asyncio lock instead
    if config.env in ["production", "development-docker"]:
        model_path =  "./services/text_embedding/embedding_models/"
    else:
        model_path = "./api/services/text_embedding/embedding_models/"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
            cls._instance.tokenizer = None
            cls._instance.timestamp = None
            cls._instance.is_loading = False
            cls._instance.model_id = None
            cls._instance.timeout = 3600
        return cls._instance

    async def get_model(self, model_id) -> AutoModel:
        if (self.model is not None and
            self.timestamp is not None and
            model_id == self.model_id and
            time.time() - self.timestamp < self.timeout):
            return self.model, self.tokenizer

        async with self._lock:
            if (self.model is not None and
                self.timestamp is not None and
                model_id == self.model_id and
                time.time() - self.timestamp < self.timeout):
                return self.model, self.tokenizer

            print("Loading embedding model...")
            self.model = await asyncio.to_thread(AutoModel.from_pretrained, os.path.join(self.model_path, model_id))
            self.tokenizer = await asyncio.to_thread(AutoTokenizer.from_pretrained, os.path.join(self.model_path, model_id))
            self.model.eval()
            self.timestamp = time.time()
            self.model_id = model_id
            print("Embedding model loaded successfully")

        return self.model, self.tokenizer

    def cleanup(self):
        with self._lock:
            if self.model is not None:
                del self.model
                self.model = None
                self.tokenizer = None
                self.timestamp = None

# Global instance
embedding_model_manager = EmbeddingModelManager()