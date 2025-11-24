#!/bin/bash

# Start the Ollama create command in the background and wait for the server to be initialized.

# Fork a subprocess in the background
(
    # Sleep for 7 seconds
    sleep 7

    #load the custom model
    ollama create codellama-7b-nxt -f /workspace/Modelfile
) &

#Start the server in foreground
ollama serve
