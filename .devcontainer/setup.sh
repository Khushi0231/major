#!/bin/bash
# DRAVIS - GitHub Codespaces Setup Script
set -e

echo "🚀 Setting up DRAVIS..."

# 1. Install Ollama
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "  ✓ Ollama installed"
else
    echo "  ✓ Ollama already installed"
fi

# 2. Start Ollama server in background
echo "🔧 Starting Ollama server..."
ollama serve &> /tmp/ollama.log &
sleep 3
echo "  ✓ Ollama server started"

# 3. Pull Mistral model (this takes a few minutes on first run)
echo "📥 Pulling Mistral 7B model (this may take 5-10 minutes on first setup)..."
ollama pull mistral
echo "  ✓ Mistral model ready"

# 4. Create Python venv and install backend deps
echo "📦 Setting up Python environment..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r backend/requirements.txt -q
echo "  ✓ Python dependencies installed"

# 5. Install frontend deps
echo "🎨 Setting up Frontend..."
cd frontend && npm install -q && cd ..
echo "  ✓ Frontend dependencies installed"

# 6. Create .env with Ollama enabled
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# LLM Provider Configuration - Codespaces
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# OpenAI (optional cloud fallback)
OPENAI_ENABLED=false
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Mock disabled (real model available)
MOCK_ENABLED=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
EOF
    echo "  ✓ Created .env with Ollama enabled"
fi

echo ""
echo "============================================"
echo "  ✅ DRAVIS setup complete!"
echo "============================================"
echo ""
echo "  Ollama: running with Mistral 7B"
echo ""
echo "  To start the app:"
echo "    bash start.sh"
echo ""
echo "  Or manually:"
echo "    Terminal 1: .venv/bin/python -m backend.main"
echo "    Terminal 2: cd frontend && npm run dev -- --host"
echo ""
