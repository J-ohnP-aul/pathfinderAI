import os

from .prompts import recommendation_summary_prompt


def generate_general_summary(context: dict, recommendations: list[dict]) -> tuple[str | None, str | None]:
    """Use the configured Gemini general-purpose model without blocking ranking."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or not recommendations:
        return None, 'Gemini is not configured; showing scored recommendations.'

    try:
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        prompt = recommendation_summary_prompt(context, recommendations)
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=180,
                ),
            )
        except ImportError:
            import google.generativeai as legacy_genai

            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={'temperature': 0.2, 'max_output_tokens': 180},
            )
        text = getattr(response, 'text', None)
        if not text:
            return None, 'Gemini returned no summary; showing scored recommendations.'
        return text.strip(), None
    except Exception:
        return None, 'Gemini could not be reached; showing scored recommendations.'
