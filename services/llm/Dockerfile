FROM ollama/ollama:latest

# Set the environment variable for the model name
ENV MODEL_NAME=mistral

# Expose the Ollama port
EXPOSE 11434

# Use a custom entrypoint script to ensure the model is pulled if it doesn't exist
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
