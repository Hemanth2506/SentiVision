import os
import random

def generate_mild_negative_examples(output_path: str, count: int = 120):
    """Generate at least `count` diverse mild‑negative review sentences and write to `output_path`.
    The sentences cover delivery, support, quality, performance, expectation mismatch, and usability complaints.
    """
    delivery_phrases = [
        "delivery took longer than expected",
        "the package arrived later than promised",
        "shipping was delayed",
        "the item arrived after the estimated date",
        "took too long to receive the order",
    ]
    support_phrases = [
        "customer service was unhelpful",
        "support response was slow",
        "the help desk did not resolve my issue",
        "the representative was not attentive",
        "the support team could be better",
    ]
    quality_phrases = [
        "the product quality is average",
        "the item feels cheap",
        "the build quality could be better",
        "materials seem subpar",
        "the finish is not impressive",
    ]
    performance_phrases = [
        "performance is slower than advertised",
        "the device runs sluggishly",
        "it works but not as fast as expected",
        "the speed could be improved",
        "it lags during usage",
    ]
    expectation_phrases = [
        "does not meet my expectations",
        "not as described in the specs",
        "the experience could be better",
        "falls short of what was promised",
        "disappointed with the overall experience",
    ]
    usability_phrases = [
        "the interface is not intuitive",
        "hard to navigate the settings",
        "user experience could be smoother",
        "the app is a bit cumbersome",
        "usability needs improvement",
    ]
    all_groups = [delivery_phrases, support_phrases, quality_phrases, performance_phrases, expectation_phrases, usability_phrases]
    adjectives = ["slightly", "somewhat", "moderately", "a bit", "fairly", "just", "reasonably"]
    sentences = []
    while len(sentences) < count:
        group = random.choice(all_groups)
        phrase = random.choice(group)
        adv = random.choice(adjectives)
        sentence = f"Not {adv} satisfied, the {phrase}."
        # Ensure uniqueness
        if sentence not in sentences:
            sentences.append(sentence)
    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for s in sentences:
            f.write(s + "\n")
    print(f"Generated {len(sentences)} mild-negative examples to {output_path}")

if __name__ == "__main__":
    # Default path inside the ml directory
    default_path = os.path.join(os.path.dirname(__file__), "extra_mild_negative.txt")
    generate_mild_negative_examples(default_path)
