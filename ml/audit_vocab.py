import pandas as pd, json, re, sys

dataset_path = r"C:/Users/paran/Downloads/Project/dataset/reviews.csv"
df = pd.read_csv(dataset_path, encoding='utf-8')
# Ensure sentiment column present
if 'sentiment' not in df.columns or 'text' not in df.columns:
    print('Dataset missing required columns')
    sys.exit(1)
# Lowercase text for case-insensitive search
terms = ["delivery", "delivered", "shipment", "shipping", "package", "arrived", "order"]
phrases = ["longer than expected", "took too long", "delayed", "late delivery", "slow shipping", "delayed shipment"]

counts = {term: {0:0,1:0,2:0} for term in terms}
phrase_counts = {phrase: [] for phrase in phrases}

for idx, row in df.iterrows():
    text = str(row['text']).lower()
    label = int(row['sentiment'])
    for term in terms:
        if term in text:
            counts[term][label] += 1
    for phrase in phrases:
        if phrase in text:
            phrase_counts[phrase].append(label)

print(json.dumps({"term_counts": counts, "phrase_labels": phrase_counts}, indent=2))
