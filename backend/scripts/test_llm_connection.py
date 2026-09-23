import asyncio
from app.core.config import settings
from app.services.llm_client import get_llm_client

async def test_llm():
    print(f"Provider: {settings.LLM_PROVIDER}")
    print(f"Base URL: {settings.LLM_BASE_URL}")
    print(f"Model: {settings.LLM_MODEL}")
    print(f"API Key prefix: {settings.LLM_API_KEY[:10]}...")

    client = get_llm_client()
    print(f"Client instance: {type(client).__name__}")

    prompt = "Generate a JSON with a single key 'message' stating 'LLM connection successful'."
    try:
        res = await client.generate_json(prompt)
        print("Success! Response:", res)
    except Exception as e:
        print("Error during LLM call:", e)

if __name__ == "__main__":
    asyncio.run(test_llm())
