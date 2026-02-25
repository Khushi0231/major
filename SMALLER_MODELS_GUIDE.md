# 📉 DRAVIS - Saving Disk Space with LLMs

This guide explains how to use the same powerful models (Llama 3.1, Mistral) while significantly reducing the disk space required for others who download or use the project.

## Option 1: The Cloud Solution (Zero Storage, High Speed) 🚀
The best way to save space is to move the model weights off the user's computer. We have added **Groq** support for this.

- **Storage Required**: 0MB (No Ollama installation or model files needed).
- **Model**: Same models as Ollama (Llama 3.1 8B, Mixstral 8x7B).
- **Speed**: Extremely fast (up to 500 tokens/sec).

### Setup:
1. Get a free API key at [console.groq.com](https://console.groq.com/).
2. Add it to your `.env` file:
   ```bash
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   ```
3. The app will automatically use Groq if available.

---

## Option 2: The Local Solution (Extreme Quantization) 📦
If you must remain offline, you can use highly compressed versions of the models. Ollama supports different "quantization" levels.

| Model Variant | Disk Space | Quality | Recommended? |
|---------------|------------|---------|--------------|
| `llama3.1:8b` (Default) | **4.7 GB** | Excellent | Yes (Desktop) |
| `llama3.1:8b-instruct-q4_K_M` | **4.9 GB** | Best 4-bit | Yes |
| `llama3.1:8b-instruct-q2_K` | **2.5 GB** | Good | **For low storage** |
| `tinyllama` | **637 MB** | Basic | For ultra-light |

### How to use:
Change the `OLLAMA_MODEL` in your `.env`:
```bash
OLLAMA_MODEL=llama3.1:8b-instruct-q2_K
```
Then pull the smaller version:
```bash
ollama pull llama3.1:8b-instruct-q2_K
```

---

## Summary for New Users
When sharing the project, recommend they use **Groq** for the fastest, smallest (0MB) experience, or the **q2_K** variant of Llama/Mistral for the best balance of local usage and disk space.
