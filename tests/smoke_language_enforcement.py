import asyncio
from types import SimpleNamespace


async def main():
    # Import inside to avoid module import side-effects during collection
    from app.services.gemini_ai import GeminiService

    # Bypass __init__ to avoid Vertex AI setup
    service = GeminiService.__new__(GeminiService)

    # Minimal attributes the service may reference
    service.rag_enabled = False

    # Bind instance methods where needed
    service.get_language_name = GeminiService.get_language_name.__get__(service, GeminiService)
    service.detect_language = GeminiService.detect_language.__get__(service, GeminiService)
    service._clean_for_voice = GeminiService._clean_for_voice.__get__(service, GeminiService)

    # Mock analyze to return a Hindi response text regardless of prompt
    async def fake_analyze(prompt: str, language: str | None = None):
        return SimpleNamespace(text="नमस्ते, यह एक परीक्षण है।")

    service.analyze = fake_analyze  # type: ignore[attr-defined]

    # Mock translation to return a fixed English translation
    async def fake_translate(text: str, target_lang: str) -> str:
        return "Hello, this is a test."

    service._translate_to_language = fake_translate  # type: ignore[attr-defined]

    # Now run voice conversation with enforced English output
    options = {
        "stt_language": "en-US",
        "force_response_language": "en-US",
        "conversation_context": "",
    }

    result = await service.process_voice_conversation(
        text="testing language enforcement",
        options=options,
        language=None,
    )

    print({"result": result})


if __name__ == "__main__":
    asyncio.run(main())
