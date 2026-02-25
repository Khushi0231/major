#!/bin/bash
set -e

echo "========================================"
echo "  DRAVIS LLM Engine Starting..."
echo "  Model: ${MODEL_NAME:-mistral}"
echo "========================================"

# Start Ollama server in the background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama API to be ready (poll with built-in wget, no curl needed)
echo "Waiting for Ollama server to be ready..."
until wget -qO- http://localhost:11434/api/tags > /dev/null 2>&1; do
  sleep 2
done
echo "[OK] Ollama server is up."

# Pull the model if not already present
MODEL="${MODEL_NAME:-mistral}"
echo "Checking for model: $MODEL"

if ollama list 2>/dev/null | grep -q "^${MODEL}"; then
  echo "[OK] Model '$MODEL' already present. Skipping download."
else
  echo "[INFO] Pulling model '$MODEL'... (This may take several minutes on first run)"
  ollama pull "$MODEL"
  echo "[OK] Model '$MODEL' downloaded successfully."
fi

echo ""
echo "========================================"
echo "  LLM Engine READY — serving $MODEL"
echo "========================================"

# Keep the container alive by waiting on the Ollama process
wait $OLLAMA_PID
