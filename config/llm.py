from crewai import LLM

llm = LLM(
    model="openrouter/mistralai/mistral-7b-instruct",
    temperature=0.0,
    max_tokens=512
)
