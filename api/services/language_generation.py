import json
import aiohttp
from db import database
import re

async def generate_language(instruction, model="qwen3-coder:30b", system=None, max_tokens=300, custom_stop_tokens: list=[]):
    if model == "default":
        model = "qwen3-coder:30b"
    settings = await database.get_settings()
    if settings.api_type == "ollama":
        text = await generate_language_ollama(instruction, model=model, system=system, max_tokens=max_tokens, custom_stop_tokens=custom_stop_tokens)
    elif settings.api_type == "open-ai":
        text = await generate_language_open_ai(instruction, model=model, system=system, max_tokens=max_tokens, custom_stop_tokens=custom_stop_tokens)
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


async def generate_language_ollama(instruction, model, system=None, max_tokens=300, custom_stop_tokens: list = []):
    ollama_url, api_token = await get_api_credentials()
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
        async with session.post(f"{ollama_url}api/generate", json=payload, headers=headers) as response:
            text = await response.text()
            try:
                text = json.loads(text)["response"]
            except Exception as e:
                print(response)
                raise e
    return(text)



async def generate_language_open_ai(instruction, model, system=None, max_tokens=300, custom_stop_tokens: list = []):
    api_url, api_token = await get_api_credentials()
    async with aiohttp.ClientSession() as session:
        payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"{system}"
                    },
                    {
                        "role": "user",
                        "content": f"{instruction}",
                    }],
                "stream": False,
                "stop": custom_stop_tokens,
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
    settings = await database.get_settings()
    return settings.api_url, settings.api_key

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
