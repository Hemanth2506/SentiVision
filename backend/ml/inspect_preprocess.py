import os
import sys

# Ensure ml package is in path
sys.path.insert(0, os.path.dirname(__file__))

from preprocess import clean_text
from sklearn.feature_extraction.text import TfidfVectorizer

SAMPLE_SENTENCE = "Not satisfied with the quality of this item."

def main():
    # Original sentence
    print("Original sentence:")
    print(SAMPLE_SENTENCE)
    # Cleaned version
    cleaned = clean_text(SAMPLE_SENTENCE)
    print("\nCleaned output (tokens joined by space):")
    print(cleaned)
    # Token list
    tokens = cleaned.split()
    print("\nTokens passed to TF-IDF:")
    print(tokens)
    # Build a temporary TF-IDF vectorizer on this single sentence to show feature names
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([cleaned])
    print("\nTF-IDF feature names (order matches vector indices):")
    print(vectorizer.get_feature_names_out())
    print("\nVector representation (sparse):")
    print(tfidf)

if __name__ == "__main__":
    main()
