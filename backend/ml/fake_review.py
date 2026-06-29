"""
SentiVision AI — Fake Review Detection Module
Analyzes reviews for suspicious patterns and computes a Trust Score.
"""

import re
import math
from collections import Counter


def detect_fake_review(text: str) -> dict:
    """
    Analyze text for fake/spam/bot review patterns.

    Checks:
    - Length (very short = suspicious)
    - ALL CAPS ratio (bot-like)
    - Repetitive words/phrases
    - Excessive punctuation
    - Extreme polarity markers (all superlatives)
    - Generic spam phrases

    Returns:
        dict: {
            'trust_score': int (0-100),
            'is_suspicious': bool,
            'flags': list of triggered flags,
            'verdict': str
        }
    """
    if not text or not text.strip():
        return {
            'trust_score': 50,
            'is_suspicious': False,
            'flags': [],
            'verdict': 'No content to analyze',
        }

    flags = []
    penalty = 0

    words = text.split()
    word_count = len(words)
    char_count = len(text)

    # ── Check 1: Extremely short review ────────────────────────────
    if word_count < 4:
        flags.append('Too short (< 4 words) — low information content')
        penalty += 30
    elif word_count < 8:
        flags.append('Very short review — limited detail')
        penalty += 15

    # ── Check 2: ALL CAPS ratio ─────────────────────────────────────
    if char_count > 10:
        upper_chars = sum(1 for c in text if c.isupper())
        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars > 0:
            caps_ratio = upper_chars / alpha_chars
            if caps_ratio > 0.7:
                flags.append(f'Excessive capitalization ({caps_ratio:.0%} caps) — bot pattern')
                penalty += 25
            elif caps_ratio > 0.4:
                flags.append(f'High capitalization ({caps_ratio:.0%} caps)')
                penalty += 10

    # ── Check 3: Repetitive words ───────────────────────────────────
    if word_count > 5:
        lower_words = [w.lower().strip('.,!?;:') for w in words]
        word_freq = Counter(lower_words)
        most_common_word, most_common_count = word_freq.most_common(1)[0]
        repetition_ratio = most_common_count / word_count
        if repetition_ratio > 0.25 and most_common_word not in {'the', 'a', 'an', 'is', 'was', 'it', 'i', 'to', 'and', 'of', 'in', 'this'}:
            flags.append(f'Highly repetitive word "{most_common_word}" ({most_common_count}x) — suspicious')
            penalty += 20
        elif repetition_ratio > 0.15 and most_common_word not in {'the', 'a', 'an', 'is', 'was', 'it', 'i', 'to', 'and', 'of', 'in', 'this'}:
            flags.append(f'Repetitive usage of "{most_common_word}"')
            penalty += 10

    # ── Check 4: Excessive punctuation ─────────────────────────────
    exclamation_count = text.count('!')
    question_count = text.count('?')
    if exclamation_count > 5:
        flags.append(f'Excessive exclamation marks ({exclamation_count}x) — spam pattern')
        penalty += 15
    elif exclamation_count > 3:
        flags.append(f'Multiple exclamation marks ({exclamation_count}x)')
        penalty += 5

    # ── Check 5: Extreme superlatives / generic spam phrases ────────
    spam_patterns = [
        r'\bbest (ever|product|buy|purchase|item)\b',
        r'\bworse?t (ever|product|buy|purchase|item)\b',
        r'\b(buy|get|order|purchase) now\b',
        r'\b(click|visit|check out) (here|this|our|my)\b',
        r'\b5 stars?\b.*\b5 stars?\b',
        r'\bperfect perfect\b',
        r'\bamazing amazing\b',
        r'\bhighly highly\b',
        r'\bwould (definitely|absolutely|certainly) recommend\b.*\bwould (definitely|absolutely|certainly) recommend\b',
    ]
    for pattern in spam_patterns:
        if re.search(pattern, text.lower()):
            flags.append(f'Spam phrase pattern detected')
            penalty += 12
            break

    # ── Check 6: Only superlatives (no details) ─────────────────────
    superlatives = ['best', 'worst', 'greatest', 'perfect', 'terrible', 'amazing',
                    'awful', 'excellent', 'horrible', 'fantastic', 'dreadful']
    if word_count > 3:
        superlative_count = sum(1 for w in words if w.lower() in superlatives)
        if superlative_count / word_count > 0.4:
            flags.append('Overuse of superlatives without substantive content')
            penalty += 15

    # ── Check 7: Gibberish / random characters ─────────────────────
    non_alpha_ratio = sum(1 for c in text if not c.isalpha() and not c.isspace()) / max(char_count, 1)
    if non_alpha_ratio > 0.4:
        flags.append('High ratio of special characters — possible gibberish')
        penalty += 20

    # ── Compute trust score ─────────────────────────────────────────
    trust_score = max(0, min(100, 100 - penalty))

    is_suspicious = trust_score < 60

    if trust_score >= 80:
        verdict = 'Likely Authentic'
    elif trust_score >= 60:
        verdict = 'Possibly Authentic'
    elif trust_score >= 40:
        verdict = 'Suspicious'
    else:
        verdict = 'Likely Fake / Spam'

    return {
        'trust_score': trust_score,
        'is_suspicious': is_suspicious,
        'flags': flags[:5],  # Cap at 5 flags for UI
        'verdict': verdict,
    }


if __name__ == '__main__':
    tests = [
        "This is the BEST BEST BEST PRODUCT EVER!!! BUY NOW BUY NOW!!!",
        "Great quality and fast shipping. Works exactly as described. Highly recommend.",
        "ok",
        "The product arrived yesterday and I started using it today.",
        "AMAZING AMAZING AMAZING AMAZING AMAZING!!!!!! BUY IT!!!!!!!",
        "Terrible terrible terrible terrible product, worst worst worst ever!!!",
    ]
    print("\n  Fake Review Detection Test:\n")
    for text in tests:
        result = detect_fake_review(text)
        print(f"  Text: \"{text[:60]}\"")
        print(f"  Trust: {result['trust_score']}/100 | Verdict: {result['verdict']}")
        if result['flags']:
            for flag in result['flags']:
                print(f"    [!] {flag}")
        print()
