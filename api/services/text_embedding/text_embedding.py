from services.text_embedding.embedding_model_manager import embedding_model_manager
import torch
from torch import Tensor

async def embed_text(text: str, instruction: str = "", model="traceformer-e5-base", provider:str="local"):
    """Apply an embedding model to a text snippet and return an embedding-vector, potentially add an instruction.

    Args:
        text (_type_): text to embed.
        instruction (_type_): If set, instruction to add to text. For query embeddings only.
        model (_type_): Name of the model to use
        provider (_type_, optional): Which of the implemented model providers to use. Defaults to local for models stored on the api server.
    """
    if not instruction=="":
        _input = get_detailed_instruct(instruction, text)
    else:
        _input = text
    if provider == "local":
        return await embed_text_local(_input, model)

async def embed_text_local(text: str, model: str):
    """Embed a text using a local model with pytorch

    Args:
        text (str): Text to embed
        model (_type_): Local model to use
    """
    model, tokenizer = await embedding_model_manager.get_model(model)
    with torch.no_grad():
        token = tokenizer(text, max_length=512, padding=True, truncation=True, return_tensors='pt')
        input_ids = token["input_ids"]
        attention_mask = token["attention_mask"]
        out = model(input_ids, attention_mask)
        embedding = average_pool(out.last_hidden_state, attention_mask)
        embedding = embedding.numpy()[0]
    return embedding

def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

def get_detailed_instruct(task_description: str, query: str) -> str:
    return f'Instruct: {task_description}\nQuery: {query}'
