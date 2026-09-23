import os
import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from .prompts import recommendation_summary_prompt


def generate_general_summary(context: dict, recommendations: list[dict]) -> tuple[str | None, str | None]:
    """Generate a summary with the configured local or hosted model."""
    if not recommendations:
        return None, 'No recommendations available for an AI summary.'

    if os.getenv('LLM_PROVIDER', 'ollama').lower() == 'ollama':
        return generate_ollama_summary(context, recommendations)

    return generate_gemini_summary(context, recommendations)


def generate_ollama_summary(context: dict, recommendations: list[dict]) -> tuple[str | None, str | None]:
    model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
    prompt = recommendation_summary_prompt(context, recommendations)
    payload = json.dumps({
        'model': model_name,
        'prompt': prompt,
        'stream': False,
        'options': {'temperature': 0.2},
    }).encode()
    request = Request(
        os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/api/generate'),
        data=payload,
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        text = result.get('response', '').strip()
        if text:
            return text, None
        return None, f'Ollama returned no summary for {model_name}; showing scored recommendations.'
    except URLError as error:
        if isinstance(error.reason, ConnectionRefusedError):
            return None, 'Ollama is not running; start it locally to enable AI summaries.'
        return None, 'Ollama could not be reached; showing scored recommendations.'
    except OSError:
        return None, 'Ollama could not be reached; showing scored recommendations.'
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None, 'Ollama returned an invalid response; showing scored recommendations.'


def generate_gemini_summary(context: dict, recommendations: list[dict]) -> tuple[str | None, str | None]:
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
            try:
                import google.generativeai as legacy_genai
            except ImportError:
                return None, 'Gemini SDK is missing from this Python environment; showing scored recommendations.'

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
    except Exception as error:
        if 'RESOURCE_EXHAUSTED' in str(error) or '429' in str(error):
            return None, 'Gemini free-tier quota is exhausted; showing scored recommendations.'
        error_name = type(error).__name__
        return None, f'Gemini request failed ({error_name}); showing scored recommendations.'
