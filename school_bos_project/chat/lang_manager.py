import json, os
from django.conf import settings

def get_lang_text(key: str, language: str = "English") -> str:
    """
    Fetch translated text from the correct JSON file based on user's language preference.
    """
    lang_code = "hi" if language.lower().startswith("hin") else "en"
    print(settings.BASE_DIR)
    path = os.path.join(settings.BASE_DIR,"chat", "lang", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, f"[Missing translation: {key}]")
    except Exception as e:
        return f"[Translation error: {e}]"
