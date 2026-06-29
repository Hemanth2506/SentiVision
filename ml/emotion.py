"""
SentiVision AI — Emotion Detection Module
Detects emotions using rule-based lexicon approach.
Maps to 8 emotion categories: Happy, Excited, Angry, Sad, Fear, Surprise, Disgust, Neutral
"""

import re
import os
import sys

# ─── Emotion lexicons ──────────────────────────────────────────────
EMOTION_LEXICONS = {
    'happy': [
        'happy', 'joy', 'joyful', 'pleased', 'glad', 'delighted', 'cheerful',
        'wonderful', 'great', 'fantastic', 'love', 'loved', 'loving', 'enjoy',
        'enjoyed', 'satisfied', 'content', 'comfortable', 'warm', 'blissful',
        'elated', 'thankful', 'grateful', 'blessed', 'smile', 'smiling',
        'laugh', 'laughing', 'celebrate', 'celebration', 'fun', 'positive',
        'good', 'nice', 'beautiful', 'lovely', 'kind', 'sweet', 'perfect',
    ],
    'excited': [
        'excited', 'exciting', 'thrill', 'thrilled', 'thrilling', 'amazing',
        'incredible', 'awesome', 'outstanding', 'excellent', 'superb', 'wow',
        'unbelievable', 'phenomenal', 'spectacular', 'brilliant', 'epic',
        'extraordinary', 'magnificent', 'impressive', 'energized', 'passionate',
        'enthusiastic', 'eager', 'pumped', 'ecstatic', 'exhilarated', 'euphoric',
        'fantastic', 'mind-blowing', 'insane', 'remarkable',
    ],
    'angry': [
        'angry', 'anger', 'furious', 'fury', 'rage', 'mad', 'irate', 'outraged',
        'frustrate', 'frustrated', 'frustrating', 'annoyed', 'annoying', 'irritated',
        'irritating', 'hate', 'hated', 'hating', 'disgust', 'disgusted',
        'horrible', 'awful', 'terrible', 'worst', 'pathetic', 'ridiculous',
        'unacceptable', 'rude', 'disrespectful', 'offensive', 'infuriating',
        'appalling', 'outrage', 'livid', 'agitated', 'hostile',
    ],
    'sad': [
        'sad', 'sadness', 'unhappy', 'miserable', 'depressed', 'depression',
        'heartbroken', 'heartbreak', 'grief', 'grieve', 'mourning', 'mourn',
        'cry', 'crying', 'tears', 'tear', 'upset', 'disappointed', 'disappointment',
        'regret', 'regretful', 'sorry', 'unfortunate', 'tragic', 'tragedy',
        'painful', 'pain', 'suffer', 'suffering', 'lonely', 'loneliness', 'alone',
        'hopeless', 'helpless', 'lost', 'empty', 'broken', 'hurt',
    ],
    'fear': [
        'fear', 'fearful', 'afraid', 'scared', 'scary', 'terrified', 'terrifying',
        'terror', 'dread', 'dreadful', 'horror', 'horrified', 'horrifying',
        'anxious', 'anxiety', 'panic', 'panicked', 'nervous', 'worry', 'worried',
        'worrying', 'concern', 'concerned', 'alarmed', 'alarming', 'threat',
        'threatened', 'dangerous', 'risk', 'risky', 'unsafe', 'vulnerable',
        'tremble', 'trembling', 'shaken', 'uneasy',
    ],
    'surprise': [
        'surprised', 'surprise', 'surprising', 'astonished', 'astonishing',
        'shocked', 'shocking', 'shock', 'unexpected', 'unbelievable', 'stunning',
        'stunned', 'jaw-dropping', 'astounded', 'amazed', 'bewildered',
        'startled', 'speechless', 'incredible', 'mind-blowing', 'sudden',
        'unexpectedly', 'never expected', 'never thought', 'out of nowhere',
        'caught off guard', 'taken aback',
    ],
    'disgust': [
        'disgusting', 'disgusted', 'disgust', 'gross', 'nasty', 'vile', 'revolting',
        'repulsive', 'repelled', 'nauseating', 'nauseous', 'sick', 'sickening',
        'yuck', 'ew', 'horrible', 'filthy', 'dirty', 'putrid', 'rotten',
        'abhorrent', 'loathe', 'loathing', 'detestable', 'appalling',
        'shameful', 'shameless', 'deplorable', 'reprehensible',
    ],
    'neutral': [
        'okay', 'fine', 'alright', 'normal', 'regular', 'average', 'standard',
        'typical', 'ordinary', 'common', 'usual', 'routine', 'basic', 'simple',
        'moderate', 'reasonable', 'acceptable', 'adequate', 'sufficient',
        'neutral', 'indifferent', 'undecided', 'uncertain', 'mixed',
    ],
}

EMOTION_EMOJIS = {
    'happy': '😊',
    'excited': '🤩',
    'angry': '😠',
    'sad': '😢',
    'fear': '😨',
    'surprise': '😮',
    'disgust': '🤢',
    'neutral': '😐',
}

EMOTION_COLORS = {
    'happy': '#22c55e',
    'excited': '#f59e0b',
    'angry': '#ef4444',
    'sad': '#3b82f6',
    'fear': '#a855f7',
    'surprise': '#ec4899',
    'disgust': '#84cc16',
    'neutral': '#6b7280',
}


def detect_emotion(text: str) -> dict:
    """
    Detect the dominant emotion in text using lexicon scoring.

    Args:
        text: Input text

    Returns:
        dict: {
            'emotion': str (e.g., 'Happy'),
            'emoji': str,
            'color': str (hex),
            'confidence': float,
            'all_emotions': {emotion: score_percent, ...}
        }
    """
    if not text or not text.strip():
        return _make_result('neutral', 50.0, {})

    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)

    # Score each emotion
    scores = {}
    for emotion, keywords in EMOTION_LEXICONS.items():
        score = 0
        for word in words:
            if word in keywords:
                score += 1
        # Also check multi-word phrases
        for keyword in keywords:
            if ' ' in keyword and keyword in text_lower:
                score += 2
        scores[emotion] = score

    total = sum(scores.values())

    if total == 0:
        # No emotional words found → neutral
        return _make_result('neutral', 70.0, {e: 0.0 for e in scores})

    # Normalize to percentages
    pct_scores = {e: round(s / total * 100, 1) for e, s in scores.items()}

    # Find dominant emotion
    dominant = max(scores.items(), key=lambda x: x[1])
    emotion_name = dominant[0]
    raw_score = dominant[1]

    # Calculate confidence based on dominance
    second_highest = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
    dominance_gap = raw_score - second_highest
    confidence = min(95.0, 50.0 + dominance_gap * 10 + (raw_score / max(len(words), 1)) * 100)

    return _make_result(emotion_name, confidence, pct_scores)


def _make_result(emotion_name: str, confidence: float, all_emotions: dict) -> dict:
    """Build the emotion result dict."""
    return {
        'emotion': emotion_name.capitalize(),
        'emoji': EMOTION_EMOJIS.get(emotion_name, '😐'),
        'color': EMOTION_COLORS.get(emotion_name, '#6b7280'),
        'confidence': round(min(confidence, 99.0), 1),
        'all_emotions': all_emotions,
    }


if __name__ == '__main__':
    tests = [
        "This product is absolutely amazing! I'm so thrilled with it!",
        "I'm really angry about this terrible service.",
        "I felt so sad reading the news today.",
        "The meeting is scheduled for Monday.",
        "I'm scared about what might happen.",
        "WOW I cannot believe this happened!",
    ]
    print("\n  Emotion Detection Test:")
    for text in tests:
        result = detect_emotion(text)
        print(f"  '{text[:50]}'")
        print(f"  -> {result['emotion']} {result['emoji']} ({result['confidence']:.0f}%)")
        print()
