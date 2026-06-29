"""
SentiVision AI — Text Preprocessing Module
Handles text cleaning, tokenization, lemmatization, and TF-IDF vectorization.
Optimized for 3-class classification (Positive / Neutral / Negative).
"""

import re
import string
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Download required NLTK resources
for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "averaged_perceptron_tagger"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

# ─── Constants ─────────────────────────────────────────────────────
STOP_WORDS = set(stopwords.words('english'))

# Words that are important sentiment indicators — keep them even if stopwords
SENTIMENT_KEEP = {
    "not", "no", "never", "neither", "nor", "nothing", "nowhere",
    "nobody", "none", "cannot", "can't", "won't", "don't", "doesn't",
    "isn't", "wasn't", "weren't", "hadn't", "haven't", "hasn't",
    "n't",
    "very", "too", "much", "most", "more", "less", "least",
    "but", "however", "although", "though", "yet", "still",
    "just", "only", "even", "really", "quite",
}

# Words that are strong indicators of neutral/factual content
NEUTRAL_INDICATORS = {
    "is", "are", "was", "were", "has", "have", "had",
    "contains", "includes", "consists", "measures", "weighs",
    "starts", "begins", "ends", "runs", "operates",
    "scheduled", "confirmed", "planned", "set", "due",
    "located", "found", "available", "supported", "required",
}

FILTERED_STOPS = STOP_WORDS - SENTIMENT_KEEP

lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Clean and preprocess a single text string.

    Pipeline:
        Lowercase → Remove URLs → Remove HTML → Remove special chars
        → Tokenize → Remove stopwords (preserve sentiment) → Lemmatize → Rejoin

    Args:
        text (str): Raw input text

    Returns:
        str: Cleaned text tokens joined by space
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', ' ', text)

    # Add Negation Handling
    text = re.sub(
        r"\b(not|never|no|wasn't|didn't|doesn't|isn't|couldn't|wouldn't|hardly|barely|neither|nor)\s+(\w+)",
        lambda m: f"{m.group(1).replace(chr(39), '')}_{m.group(2)}",
        text
    )

    # Normalize whitespace and punctuation
    text = re.sub(r'[^\w\s\'-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Filter and lemmatize
    cleaned_tokens = []
    for token in tokens:
        # Skip pure numbers (neutral factual indicators kept via context)
        if re.match(r'^\d+$', token) and len(token) > 6:
            continue
        # Skip very short tokens
        if len(token) < 2:
            continue
        # Keep token if not a stopword, or if it's a sentiment-important word
        if token not in FILTERED_STOPS or token in SENTIMENT_KEEP:
            lemmatized = lemmatizer.lemmatize(token, pos='v')
            lemmatized = lemmatizer.lemmatize(lemmatized, pos='n')
            cleaned_tokens.append(lemmatized)

    return ' '.join(cleaned_tokens)


def preprocess_corpus(texts: list) -> list:
    """
    Preprocess a list of texts.

    Args:
        texts (list): List of raw text strings

    Returns:
        list: List of cleaned text strings
    """
    print(f"  Preprocessing {len(texts)} texts...")
    cleaned = [clean_text(t) for t in texts]
    empty_count = sum(1 for c in cleaned if not c.strip())
    if empty_count:
        print(f"  Warning: {empty_count} texts became empty after cleaning.")
    return cleaned


def build_tfidf_vectorizer(cleaned_texts: list, max_features: int = 20000):
    """
    Build and fit a TF-IDF vectorizer on cleaned texts.

    Optimized for 3-class sentiment:
    - Higher max_features to capture neutral/factual vocabulary
    - Bigrams included to capture negation patterns
    - Sublinear TF to reduce the weight of very frequent terms

    Args:
        cleaned_texts (list): List of preprocessed text strings
        max_features (int): Maximum number of features

    Returns:
        tuple: (fitted_vectorizer, feature_matrix)
    """
    print(f"  Building TF-IDF vectorizer (max_features={max_features})...")
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 3),       # Unigrams + bigrams + trigrams for better neutral capture
        min_df=2,                  # Ignore very rare terms
        max_df=0.95,               # Ignore very common terms
        sublinear_tf=True,         # log(1+tf) — reduces dominance of frequent terms
        analyzer='word',
        token_pattern=r"(?u)\b\w[\w'-]*\b",
    )
    features = vectorizer.fit_transform(cleaned_texts)
    print(f"  Vectorizer built: {features.shape[1]} features, {features.shape[0]} samples.")
    return vectorizer, features


def save_vectorizer(vectorizer, path: str):
    """Save fitted vectorizer to disk."""
    joblib.dump(vectorizer, path)
    print(f"  Vectorizer saved to: {path}")


def load_vectorizer(path: str):
    """Load vectorizer from disk."""
    return joblib.load(path)
