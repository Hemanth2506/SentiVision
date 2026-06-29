import os, sys
sys.path.insert(0, os.path.abspath('ml'))
from predict import predict_sentiment

sentences = [
    "The package contains two items.",
    "The meeting is scheduled for Monday.",
    "Delivery took longer than expected.",
    "Not satisfied with the quality of this item.",
    "Customer service was unhelpful"
]
for s in sentences:
    res = predict_sentiment(s)
    probs = res['probabilities']
    print(f"Sentence: {s}")
    print(f"  Raw probabilities: {probs}")
    print(f"  Sentiment (after gating): {res['sentiment']} ({res['confidence']:.1f}%)")
    print()
