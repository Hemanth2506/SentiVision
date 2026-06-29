"""
SentiVision AI — Language Detection & Translation Module
Detects language using langdetect, translates using deep_translator.
Supports: English, Hindi, Tamil, Kannada, Telugu, Malayalam, + many others.
"""

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'kn': 'Kannada',
    'te': 'Telugu',
    'ml': 'Malayalam',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'ar': 'Arabic',
    'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian',
    'it': 'Italian',
}

LANGUAGE_FLAGS = {
    'en': '🇺🇸', 'hi': '🇮🇳', 'ta': '🇮🇳', 'kn': '🇮🇳',
    'te': '🇮🇳', 'ml': '🇮🇳', 'fr': '🇫🇷', 'de': '🇩🇪',
    'es': '🇪🇸', 'pt': '🇧🇷', 'ar': '🇸🇦', 'zh-cn': '🇨🇳',
    'ja': '🇯🇵', 'ko': '🇰🇷', 'ru': '🇷🇺', 'it': '🇮🇹',
}


def detect_language(text: str) -> dict:
    """
    Detect the language of the input text.

    Args:
        text: Input text

    Returns:
        dict: {
            'language_code': str,
            'language_name': str,
            'flag': str,
            'is_english': bool,
            'confidence': str (high/medium/low)
        }
    """
    if not text or len(text.strip()) < 3:
        return {
            'language_code': 'en',
            'language_name': 'English',
            'flag': '🇺🇸',
            'is_english': True,
            'confidence': 'low',
        }

    try:
        from langdetect import detect, detect_langs
        from langdetect import DetectorFactory
        DetectorFactory.seed = 42  # Deterministic results

        lang_code = detect(text)
        lang_probs = detect_langs(text)

        # Confidence based on probability
        top_prob = lang_probs[0].prob if lang_probs else 0.5
        if top_prob > 0.9:
            confidence = 'high'
        elif top_prob > 0.7:
            confidence = 'medium'
        else:
            confidence = 'low'

        lang_name = SUPPORTED_LANGUAGES.get(lang_code, lang_code.upper())
        flag = LANGUAGE_FLAGS.get(lang_code, '🌐')

        return {
            'language_code': lang_code,
            'language_name': lang_name,
            'flag': flag,
            'is_english': lang_code == 'en',
            'confidence': confidence,
        }

    except Exception as e:
        return {
            'language_code': 'en',
            'language_name': 'English',
            'flag': '🇺🇸',
            'is_english': True,
            'confidence': 'low',
            'error': str(e),
        }


def translate_to_english(text: str, source_lang: str = 'auto') -> dict:
    """
    Translate text to English using deep_translator.

    Args:
        text: Input text to translate
        source_lang: Source language code (or 'auto' for auto-detect)

    Returns:
        dict: {
            'original_text': str,
            'translated_text': str,
            'source_language': str,
            'was_translated': bool,
            'error': str (optional)
        }
    """
    if not text or not text.strip():
        return {
            'original_text': text,
            'translated_text': text,
            'source_language': 'en',
            'was_translated': False,
        }

    try:
        from deep_translator import GoogleTranslator

        # Detect language if not specified
        if source_lang == 'auto':
            lang_info = detect_language(text)
            source_lang = lang_info.get('language_code', 'en')

        # If already English, skip translation
        if source_lang == 'en':
            return {
                'original_text': text,
                'translated_text': text,
                'source_language': 'en',
                'was_translated': False,
            }

        # Translate to English
        # deep_translator handles long texts better than googletrans
        translator = GoogleTranslator(source=source_lang, target='en')

        # Handle long texts by chunking
        if len(text) > 4500:
            chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            translated = ' '.join(translated_chunks)
        else:
            translated = translator.translate(text)

        return {
            'original_text': text,
            'translated_text': translated or text,
            'source_language': source_lang,
            'was_translated': True,
        }

    except Exception as e:
        return {
            'original_text': text,
            'translated_text': text,
            'source_language': source_lang,
            'was_translated': False,
            'error': f'Translation unavailable: {str(e)}',
        }


def analyze_language(text: str) -> dict:
    """
    Full pipeline: detect language + translate if needed.

    Returns combined language analysis result.
    """
    lang_info = detect_language(text)

    if lang_info['is_english']:
        return {
            **lang_info,
            'original_text': text,
            'translated_text': text,
            'was_translated': False,
        }

    translation = translate_to_english(text, source_lang=lang_info['language_code'])

    return {
        **lang_info,
        'original_text': text,
        'translated_text': translation.get('translated_text', text),
        'was_translated': translation.get('was_translated', False),
        'translation_error': translation.get('error'),
    }


if __name__ == '__main__':
    tests = [
        "This product is absolutely amazing!",
        "यह उत्पाद बहुत अच्छा है।",  # Hindi
        "இந்த தயாரிப்பு மிகவும் நன்றாக உள்ளது",  # Tamil
    ]
    print("\n  Language Detection Test:\n")
    for text in tests:
        result = analyze_language(text)
        print(f"  Text: \"{text}\"")
        print(f"  Language: {result['flag']} {result['language_name']} ({result['language_code']})")
        if result.get('was_translated'):
            print(f"  Translated: \"{result['translated_text']}\"")
        print()
