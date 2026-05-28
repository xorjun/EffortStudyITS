import json
import aiohttp
from db import database
from config import config
import re

OPENAI_COMPATIBLE_API_TYPES = {"open-ai", "mistral"}


def _normalize_api_url(api_url: str) -> str:
    if api_url == "":
        return api_url
    return api_url if api_url.endswith("/") else f"{api_url}/"


async def get_language_generation_settings() -> tuple[str, str, str | None]:
    settings = await database.get_settings()
    api_type = (settings.api_type or config.llm_api_type or "").strip().lower()
    api_url = _normalize_api_url((settings.api_url or config.llm_api_url or "").strip())
    api_key = settings.api_key if settings.api_key not in [None, ""] else (config.llm_api_key or None)
    return api_type, api_url, api_key


async def get_pedagogical_system_prompt(base_system: str | None = None) -> str | None:
    settings = await database.get_settings()
    admin_system_prompt = (settings.pedagogical_system_prompt or "").strip()
    if admin_system_prompt and base_system:
        return f"{base_system.strip()}\n\nAdditional pedagogical instructions from the administrator:\n{admin_system_prompt}"
    if admin_system_prompt:
        return admin_system_prompt
    return base_system


async def has_language_generation_configuration() -> bool:
    api_type, api_url, api_key = await get_language_generation_settings()
    if api_type == "" or api_url == "":
        return False
    if api_type in OPENAI_COMPATIBLE_API_TYPES and not api_key:
        return False
    return True


def _resolve_default_model(api_type: str) -> str:
    if config.llm_default_model:
        return config.llm_default_model
    if api_type == "mistral":
        return "mistral-small-latest"
    if api_type == "open-ai":
        return "gpt-4o-mini"
    return "qwen3-coder:30b"


async def generate_language(instruction, model="qwen3-coder:30b", system=None, max_tokens=300, custom_stop_tokens: list | None = None):
    api_type, api_url, api_token = await get_language_generation_settings()
    if model == "default":
        model = _resolve_default_model(api_type)
    if api_type == "ollama":
        text = await generate_language_ollama(
            instruction,
            model=model,
            api_url=api_url,
            api_token=api_token,
            system=system,
            max_tokens=max_tokens,
            custom_stop_tokens=custom_stop_tokens,
        )
    elif api_type in OPENAI_COMPATIBLE_API_TYPES:
        text = await generate_language_open_ai(
            instruction,
            model=model,
            api_url=api_url,
            api_token=api_token,
            system=system,
            max_tokens=max_tokens,
            custom_stop_tokens=custom_stop_tokens,
        )
    else:
        raise Exception("Invalid API-type")
    return text


#async def generate_language_ollama(instruction, model, system=None, max_tokens=300):
#    ollama_url = await get_ollama_url()
#    async with aiohttp.ClientSession() as session:
#        payload = {
#                "model": model,
#                "prompt": instruction,
#                "stream": False,
#                "options": {"num_predict": max_tokens,
#                            "stop": ["<s>", "</s>", "[INST]", "[/INST]", "<<SYS>>", "<</SYS>>", "[task end]", "<|eot_id|>"]}
#            }
#        if not system is None:
#            payload["system"] = system
#        async with session.post(f"{ollama_url}api/generate", json=payload) as response:
#            text = await response.text()
#            text = json.loads(text)["response"]
#    return(text)


async def generate_language_ollama(instruction, model, api_url, api_token=None, system=None, max_tokens=300, custom_stop_tokens: list | None = None):
    custom_stop_tokens = custom_stop_tokens or []
    async with aiohttp.ClientSession() as session:
        payload = {
                "model": model,
                "prompt": instruction,
                "stream": False,
                "think": False,
                "stop": custom_stop_tokens,
            }
        if not api_token is None:
            headers = {"Authorization": f"Bearer {api_token}"}
        else: 
            headers = {}
        if not system is None:
            payload["system"] = system
        async with session.post(f"{api_url}api/generate", json=payload, headers=headers) as response:
            text = await response.text()
            try:
                text = json.loads(text)["response"]
            except Exception as e:
                print(response)
                raise e
    return(text)



async def generate_language_open_ai(instruction, model, api_url, api_token=None, system=None, max_tokens=300, custom_stop_tokens: list | None = None):
    custom_stop_tokens = custom_stop_tokens or []
    messages = []
    if system is not None:
        messages.append(
            {
                "role": "system",
                "content": system,
            }
        )
    messages.append(
        {
            "role": "user",
            "content": instruction,
        }
    )
    async with aiohttp.ClientSession() as session:
        payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "stop": custom_stop_tokens,
                "max_tokens": max_tokens,
            }
        if not api_token is None:
            headers = {"Authorization": f"Bearer {api_token}"}
        else: 
            headers = {}
        async with session.post(f"{api_url}chat/completions", json=payload, headers=headers) as response:
            response = await response.text()
            response = json.loads(response)
            try: 
                message = response["choices"][0]["message"]
                text = message["content"]
            except Exception as e:
                print(response)
                raise e
    return(text)

async def get_api_credentials():
    _, api_url, api_key = await get_language_generation_settings()
    return api_url, api_key

def parse_code_response(code_response: str):
    python_pattern = r'```python\n(.*?)```'
    general_pattern = r'```(?:[a-zA-Z0-9_+-]*)\n(.*?)```'
    if "```python" in code_response:
            match = re.search(python_pattern, code_response, re.DOTALL)
            if match:
                return match.group(1).strip().strip("`").strip()
            else:
                return code_response.split("```python")[1].strip().strip("`").strip()
    else: 
        match  = re.search(general_pattern, code_response, re.DOTALL)
        if match: 
            return match.group(1).strip().strip("`").strip()
        else:
            return code_response.strip().strip("`").strip()
