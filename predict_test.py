import sys
sys.path.append(r'C:/Users/paran/Downloads/Project/ml')
from predict import predict_sentiment

sentences = [
    "The product stopped working after a week.",
    "Delivery took longer than expected.",
    "Not satisfied with the quality of this item.",
    "Customer service was unhelpful when I called.",
    "This is the worst purchase I've made in years."
]

for s in sentences:
    result = predict_sentiment(s)
    probs = result['probabilities']
    print(f"Sentence: {s}")
    print(f"Probabilities (Positive/Neutral/Negative): {probs['positive']:.2f}%, {probs['neutral']:.2f}%, {probs['negative']:.2f}%")
    print()
