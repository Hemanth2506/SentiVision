import os
import pandas as pd
import re

# Paths (relative to this script)
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'reviews.csv')
CLEANED_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'reviews_cleaned.csv')

# Contamination keywords (case‑insensitive)
CONTAMINATION_KEYWORDS = [
    'delayed',
    'longer than expected',
    'issue',
    'problem',
    'slow',
    'broken',
    'stopped working',
    'complaint'
]

def contains_contamination(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CONTAMINATION_KEYWORDS)

def clean_and_save(dataset_path: str = DATASET_PATH, cleaned_path: str = CLEANED_PATH, keywords=None) -> None:
    """Load the original CSV, re‑label contaminated neutral rows as Negative, and save.
    Parameters
    ----------
    dataset_path: str
        Path to the original `reviews.csv`.
    cleaned_path: str
        Destination for the cleaned CSV.
    keywords: list | None
        Optional custom contamination list; if provided it overrides the module constant.
    """
    if keywords:
        global CONTAMINATION_KEYWORDS
        CONTAMINATION_KEYWORDS = keywords
    print('Loading dataset for neutral cleanup...')
    df = pd.read_csv(dataset_path)
    # Identify neutral rows
    neutral_mask = df['sentiment'] == 1
    contaminated = df[neutral_mask & df['text'].apply(contains_contamination)]
    print(f'Found {len(contaminated)} contaminated neutral examples.')
    if len(contaminated) > 0:
        print('Sample contaminated rows:')
        print(contaminated[['text']].head())
        # Re‑label as Negative (0)
        df.loc[contaminated.index, 'sentiment'] = 0
    else:
        print('No contamination found.')
    df.to_csv(cleaned_path, index=False)
    print(f'Cleaned dataset saved to {cleaned_path}')

def main():
    clean_and_save()

if __name__ == '__main__':
    main()
