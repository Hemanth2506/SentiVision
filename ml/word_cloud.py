"""
SentiVision AI — Word Cloud Generator
Generates word cloud images from text data, returned as base64 PNGs.
"""

import io
import base64
import re
from collections import Counter

# Common stop words to exclude
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'it', 'its', "it's",
    'this', 'that', 'these', 'those', 'i', 'my', 'me', 'we', 'our', 'you',
    'your', 'he', 'she', 'they', 'them', 'his', 'her', 'their', 'what',
    'which', 'who', 'how', 'when', 'where', 'why', 'so', 'if', 'then',
    'than', 'as', 'up', 'out', 'about', 'into', 'through', 'not', 'no',
    'very', 'just', 'also', 'only', 'even', 'more', 'most', 'all', 'any',
    'each', 'there', 'here', 'now', 'still', 'get', 'got', 'go', 'going',
    'came', 'come', 'said', 'say', 'one', 'two', 'three', 'product',
}

SENTIMENT_COLORS = {
    'positive': ['#22c55e', '#16a34a', '#15803d', '#86efac', '#4ade80', '#6ee7b7'],
    'negative': ['#ef4444', '#dc2626', '#b91c1c', '#fca5a5', '#f87171', '#fb923c'],
    'neutral': ['#6366f1', '#4f46e5', '#818cf8', '#a5b4fc', '#c7d2fe', '#8b5cf6'],
    'emotion': ['#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#10b981', '#f97316'],
    'all': ['#6366f1', '#22c55e', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'],
}


def _clean_for_wordcloud(texts: list) -> list:
    """Extract and clean words from texts."""
    all_words = []
    for text in texts:
        if not isinstance(text, str):
            continue
        text_lower = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
        all_words.extend(filtered)
    return all_words


def generate_word_cloud(
    texts: list,
    cloud_type: str = 'all',
    width: int = 800,
    height: int = 400,
    max_words: int = 80,
) -> str:
    """
    Generate a word cloud image from a list of texts.

    Args:
        texts: List of text strings
        cloud_type: 'positive', 'negative', 'neutral', 'emotion', or 'all'
        width: Image width in pixels
        height: Image height in pixels
        max_words: Maximum number of words to include

    Returns:
        str: Base64-encoded PNG image, or empty string on failure
    """
    if not texts:
        return ''

    try:
        from wordcloud import WordCloud
        import numpy as np
        from PIL import Image

        # Get color palette
        colors = SENTIMENT_COLORS.get(cloud_type, SENTIMENT_COLORS['all'])

        # Create color function
        def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
            import random
            return random.choice(colors)

        # Clean text
        words = _clean_for_wordcloud(texts)
        if not words:
            return ''

        text_for_cloud = ' '.join(words)

        # Generate word cloud
        wc = WordCloud(
            width=width,
            height=height,
            background_color='#0f172a',  # Dark navy background
            max_words=max_words,
            color_func=color_func,
            prefer_horizontal=0.7,
            min_font_size=10,
            max_font_size=100,
            collocations=False,
            regexp=r'\b[a-zA-Z]{3,}\b',
        )

        wc.generate(text_for_cloud)

        # Convert to base64
        buffer = io.BytesIO()
        wc.to_image().save(buffer, format='PNG', optimize=True)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f'data:image/png;base64,{img_base64}'

    except ImportError:
        # wordcloud not installed — return placeholder
        return _generate_placeholder_cloud(texts, cloud_type, width, height)
    except Exception as e:
        print(f"  Word cloud generation error: {e}")
        return _generate_placeholder_cloud(texts, cloud_type, width, height)


def get_word_frequencies(texts: list, top_n: int = 20) -> list:
    """
    Get top word frequencies from texts.

    Returns:
        list: [{'word': str, 'count': int}, ...]
    """
    words = _clean_for_wordcloud(texts)
    counter = Counter(words)
    return [
        {'word': word, 'count': count}
        for word, count in counter.most_common(top_n)
    ]


def _generate_placeholder_cloud(texts, cloud_type, width, height) -> str:
    """Generate a simple frequency-based text visualization as PNG."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random

        words = _clean_for_wordcloud(texts)
        counter = Counter(words)
        top_words = counter.most_common(40)

        if not top_words:
            return ''

        colors = SENTIMENT_COLORS.get(cloud_type, SENTIMENT_COLORS['all'])

        img = Image.new('RGB', (width, height), color='#0f172a')
        draw = ImageDraw.Draw(img)

        max_count = top_words[0][1] if top_words else 1

        for i, (word, count) in enumerate(top_words):
            font_size = int(12 + (count / max_count) * 50)
            x = random.randint(50, width - 150)
            y = random.randint(20, height - 50)
            color = random.choice(colors)
            try:
                draw.text((x, y), word, fill=color)
            except Exception:
                pass

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
    except Exception:
        return ''


if __name__ == '__main__':
    sample_texts = [
        "Amazing product excellent quality wonderful experience",
        "Terrible service broken item waste of money",
        "The meeting is scheduled for Monday",
        "Great quality fast delivery highly recommend",
        "Worst purchase ever do not buy this awful",
    ]
    result = generate_word_cloud(sample_texts, cloud_type='all')
    print(f"  Word cloud generated: {'Yes' if result else 'No'} ({len(result)} chars)")
    freqs = get_word_frequencies(sample_texts, top_n=5)
    print(f"  Top words: {freqs}")
