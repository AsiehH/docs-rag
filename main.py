from app.generate import ask

answer = ask("What is the competitor to OpenAI?")
print(f"✅ Answer: {answer}")

questions = [
    "What is a RAG pipeline?",
    "What is the capital of France?",
]

for question in questions:
    print(f"Q: {question}")
    print(f"A: {ask(question)}")
    print()
