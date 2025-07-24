# Ollama docker container that automatically loads a custom model.
FROM ollama/ollama:latest

RUN mkdir -p ./models

COPY codellama-7b-nxt.gguf /workspace/models/  
#COPY adapter-model.ggml.bin /workspace/models/

#RUN echo "FROM /home/models/codellama-7b-nxt-gguf" > /home/Modelfile

COPY Modelfile /workspace/Modelfile

COPY ollama_run_and_create.sh /workspace 

# Make the startup script executable
RUN chmod +x /workspace/ollama_run_and_create.sh

ENTRYPOINT ["/workspace/ollama_run_and_create.sh"]
