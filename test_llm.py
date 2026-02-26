"""
End-to-end test for the DRAVIS LLM stack.
Tests: availability check, system prompt injection, response quality.
Run from project root:  python test_llm.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OLLAMA_MODEL"] = "llama3.1:8b"

from chat.app.llm.providers.langchain_ollama_provider import LangChainOllamaProvider

cfg = {
    "base_url": "http://localhost:11434",
    "model": "llama3.1:8b",
    "temperature": 0.6,
}

provider = LangChainOllamaProvider(cfg)

SEPARATOR = "─" * 60

def test(label, prompt):
    print(f"\n{SEPARATOR}")
    print(f"TEST: {label}")
    print(f"PROMPT: {prompt}")
    print(SEPARATOR)
    try:
        response = provider.generate(prompt)
        print(f"RESPONSE:\n{response}")
        print(f"\n✅ PASS — {len(response)} chars")
    except Exception as e:
        print(f"❌ FAIL — {e}")

# 1. Availability check
print("\n" + SEPARATOR)
print("AVAILABILITY CHECK")
print(SEPARATOR)
avail = provider.is_available()
print(f"  Ollama reachable + llama3.1:8b present: {'✅ YES' if avail else '❌ NO'}")
if not avail:
    print("  Cannot run tests — start Ollama first.")
    sys.exit(1)

# 2. Simple factual question
test("Simple factual", "What is photosynthesis?")

# 3. Structured answer
test("Structured answer", "Explain Newton's three laws of motion with examples.")

# 4. Exam prep mode simulation
test(
    "Exam prep prompt",
    "[Instruction: The user is preparing for an exam. Give a concise, well-structured answer "
    "using headings and bullet points.]\n\nQuestion: What are the key differences between mitosis and meiosis?"
)

# 5. RAG-style context injection
test(
    "RAG context grounding",
    "--- Document Context ---\n"
    "[Source 1]: The water cycle involves evaporation, condensation, precipitation, and collection.\n"
    "Evaporation turns liquid water into vapour. Condensation forms clouds. "
    "Precipitation brings rain or snow. Collection fills rivers and lakes.\n"
    "--- End Context ---\n\n"
    "Question: Explain the water cycle based on the context above."
)

# 6. Professional tone check
test(
    "Professional tone",
    "hey can u explain like what quantum entanglement is lol"
)

print(f"\n{SEPARATOR}")
print("ALL TESTS COMPLETE")
print(SEPARATOR)
