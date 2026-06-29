"""
SentiVision AI — Balanced 3-Class Dataset Generator
Generates Positive / Neutral / Negative training data.

Labels: 0 = Negative, 1 = Neutral, 2 = Positive
"""

import os
import sys
import random
import pandas as pd
import nltk

# ─── NLTK downloads ────────────────────────────────────────────────
for pkg in ["movie_reviews", "stopwords", "punkt", "averaged_perceptron_tagger", "wordnet"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from nltk.corpus import movie_reviews

# ─── Output path ───────────────────────────────────────────────────
DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'dataset')
OUTPUT_PATH = os.path.join(DATASET_DIR, 'reviews.csv')
os.makedirs(DATASET_DIR, exist_ok=True)

TARGET_PER_CLASS = 6000
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


# ─── Neutral Sentences ─────────────────────────────────────────────
NEUTRAL_SENTENCES = [
    # Scheduling / Meetings
    "The meeting is scheduled for Monday.",
    "The event starts at 10 AM.",
    "The conference call is at 3 PM tomorrow.",
    "The deadline is set for next Friday.",
    "The appointment has been rescheduled to Wednesday.",
    "The session will last approximately two hours.",
    "The presentation is planned for Thursday morning.",
    "The seminar begins at noon.",
    "The workshop is confirmed for next Tuesday.",
    "The interview is at 9:30 AM on Monday.",
    "The exam starts at 10 AM sharp.",
    "The class is every Tuesday and Thursday.",
    "The lecture begins at 2 PM in room 305.",
    "The meeting was postponed to the following week.",
    "The annual review is scheduled for December.",
    "The project kickoff is on the first day of the month.",
    "The training session runs from 9 AM to 5 PM.",
    "The board meeting is scheduled quarterly.",
    "The review meeting will take place on Friday.",
    "The department meets every Monday at 8 AM.",

    # Product Specifications
    "The laptop has 16GB RAM and a 512GB SSD.",
    "The phone comes with a 6.5 inch display.",
    "The device supports USB-C charging.",
    "The battery capacity is 4000 mAh.",
    "The monitor has a resolution of 1920 by 1080.",
    "The processor runs at 3.2 GHz.",
    "The storage capacity is 256 gigabytes.",
    "The keyboard is available in two color options.",
    "The tablet weighs approximately 500 grams.",
    "The camera has a 12-megapixel resolution.",
    "The screen refresh rate is 120 Hz.",
    "The router supports dual-band WiFi.",
    "The speaker has an output of 20 watts.",
    "The car has a fuel tank capacity of 60 liters.",
    "The headphones have a frequency range of 20 to 20000 Hz.",
    "The software requires a minimum of 4 GB of RAM.",
    "The hard drive has a read speed of 550 MB per second.",
    "The lens has a focal length of 50mm.",
    "The power supply unit has an output of 650 watts.",
    "The cable length is 1.8 meters.",
    "The product dimensions are 30 by 20 by 10 centimeters.",
    "The device operates on a voltage of 110 to 240 volts.",
    "The printer can handle paper sizes up to A3.",
    "The graphics card has 8 GB of VRAM.",
    "The machine supports up to 32 GB of RAM.",

    # Factual Descriptions
    "The package contains two items.",
    "The product arrived yesterday and I started using it today.",
    "The box includes a charger and a user manual.",
    "The item was delivered in standard packaging.",
    "The order was placed three days ago.",
    "The shipment is currently in transit.",
    "The delivery is expected within three to five business days.",
    "The tracking number has been sent to your email.",
    "The return window is 30 days from the date of purchase.",
    "The product is available in three sizes.",
    "The manual is written in English and Spanish.",
    "The warranty covers manufacturing defects for one year.",
    "The item is sold separately from the accessories.",
    "The product is made from recycled materials.",
    "The label contains the ingredient list and nutritional values.",
    "The receipt shows the total amount paid.",
    "The invoice number is printed on the top right corner.",
    "The serial number is located on the back of the device.",
    "The user manual can be downloaded from the official website.",
    "The item was restocked last week.",

    # Neutral News / Facts
    "The company reported earnings of five billion dollars this quarter.",
    "The population of the city is approximately three million people.",
    "The temperature today is 22 degrees Celsius.",
    "The study involved 500 participants over six months.",
    "The data shows a 5 percent increase compared to last year.",
    "The survey was conducted in 30 countries.",
    "The report was published in the scientific journal last week.",
    "The election results will be announced on Tuesday.",
    "The government approved the budget for the fiscal year.",
    "The bill was signed into law on Monday.",
    "The team has 11 players on the field.",
    "The flight departs at 6:45 AM from terminal three.",
    "The train arrives at platform seven at 4:15 PM.",
    "The bridge connects the two sections of the city.",
    "The river flows south toward the sea.",
    "The museum is open from 9 AM to 5 PM on weekdays.",
    "The library has over one million books in its collection.",
    "The university was founded in 1887.",
    "The building has 40 floors.",
    "The road is 12 kilometers long.",
    "The population density is 200 people per square kilometer.",
    "The annual report was released to the public last Tuesday.",
    "The speed limit on this road is 60 kilometers per hour.",
    "The total area of the park is 150 hectares.",
    "The country borders three other nations.",
    "The monthly subscription costs ten dollars.",
    "The interest rate remained unchanged this quarter.",
    "The project has a budget of two million dollars.",
    "The distance between the two cities is 300 kilometers.",
    "The experiment lasted for 48 hours.",

    # Neutral Descriptions / Wikipedia style
    "Water is a chemical compound with the formula H2O.",
    "The Earth orbits the Sun once every 365 days.",
    "The human body contains approximately 37 trillion cells.",
    "Light travels at approximately 300,000 kilometers per second.",
    "The moon is approximately 384,400 kilometers from Earth.",
    "Carbon dioxide is a greenhouse gas.",
    "Python is a high-level programming language.",
    "Machine learning is a subset of artificial intelligence.",
    "The internet was invented in the late 20th century.",
    "DNA is a double-helix structure found in the nucleus of cells.",
    "The speed of sound is approximately 343 meters per second.",
    "A kilogram is the base unit of mass in the metric system.",
    "The periodic table contains 118 elements.",
    "Mount Everest is the highest mountain on Earth.",
    "The Amazon River is the largest river by discharge in the world.",

    # Instructions / Neutral Imperatives
    "Press the power button to turn on the device.",
    "Click the submit button to complete the form.",
    "Enter your email address and password to log in.",
    "Select the option from the dropdown menu.",
    "Scroll down to view more results.",
    "The file has been saved to the downloads folder.",
    "The update will be installed on the next restart.",
    "Your session will expire in 10 minutes.",
    "The form requires all fields to be completed.",
    "Please enter a valid email address.",
    "The password must be at least eight characters long.",
    "The account has been successfully created.",
    "Your changes have been saved.",
    "The operation completed successfully.",
    "The request is being processed.",

    # Neutral Comparative / Observational
    "The old model weighs more than the new version.",
    "The second edition includes an additional chapter.",
    "The morning shift starts two hours earlier than the afternoon shift.",
    "The north wing of the building is currently closed for renovation.",
    "The price has been updated to reflect the current exchange rate.",
    "The results vary depending on the input parameters.",
    "The system requires a reboot after installation.",
    "The file size is 2.3 gigabytes.",
    "The application supports both Windows and macOS.",
    "The version number is displayed in the settings menu.",
    "The username must be unique within the system.",
    "The report is generated in PDF format.",
    "The database is updated every 24 hours.",
    "The API returns a JSON response.",
    "The function takes two arguments and returns a boolean.",
    "The list contains 50 items.",
    "The table has five columns and twelve rows.",
    "The graph shows data for the past six months.",
    "The chart displays the monthly average.",
    "The index starts at zero.",

    # More neutral everyday statements
    "I received an email from the support team today.",
    "The package was left at the front door.",
    "The store closes at 9 PM on weekdays.",
    "The movie starts in twenty minutes.",
    "The flight is on time according to the airline website.",
    "The bus stop is two blocks away.",
    "The office is on the fourth floor.",
    "The nearest ATM is across the street.",
    "The form can be submitted online or by mail.",
    "The refund will be processed within five to seven business days.",
]


def load_movie_reviews():
    """Load NLTK movie reviews corpus (positive and negative)."""
    print("\n  Loading NLTK movie_reviews corpus...")

    pos_texts = []
    neg_texts = []

    for fileid in movie_reviews.fileids('pos'):
        text = movie_reviews.raw(fileid)
        pos_texts.append(text.replace('\n', ' ').strip())

    for fileid in movie_reviews.fileids('neg'):
        text = movie_reviews.raw(fileid)
        neg_texts.append(text.replace('\n', ' ').strip())

    print(f"  Loaded {len(pos_texts)} positive, {len(neg_texts)} negative reviews.")
    return pos_texts, neg_texts


def augment_to_target(texts, target, label_name):
    """Augment by repeating with small variations if we don't have enough samples."""
    while len(texts) < target:
        sample = random.choice(texts)
        # Simple augmentation: truncate to first sentence or shuffle sentences
        sentences = sample.split('.')
        random.shuffle(sentences)
        texts.append('.'.join(sentences).strip())
    return texts[:target]


def build_neutral_texts(target):
    """Build neutral dataset from handcrafted + augmented sentences."""
    print(f"\n  Building {target} neutral sentences...")

    # Use the curated list
    base = list(NEUTRAL_SENTENCES)

    # Augment: create variations
    augmented = []
    templates_time = [
        "The {} is set for {}.",
        "The {} has been scheduled for {}.",
        "The {} will take place on {}.",
        "The {} begins at {}.",
        "The {} is confirmed for {}.",
    ]
    events = ["meeting", "conference", "presentation", "seminar", "workshop",
              "interview", "review", "briefing", "session", "call",
              "training", "orientation", "ceremony", "event", "webinar"]
    times = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "9 AM", "10 AM", "2 PM", "3:30 PM", "noon",
             "next week", "next month", "the 15th", "the first day of the quarter",
             "the end of the month"]
    for _ in range(600):
        t = random.choice(templates_time)
        augmented.append(t.format(random.choice(events), random.choice(times)))

    templates_spec = [
        "The {} has a {} of {}.",
        "The device supports {} up to {}.",
        "The product comes with {} {}.",
        "The system requires {} of {}.",
        "The {} weighs approximately {} {}.",
    ]
    parts = ["storage", "battery", "display", "processor", "RAM", "weight", "speed", "resolution"]
    vals = ["256GB", "512GB", "1TB", "8GB", "16GB", "32GB",
            "120Hz", "4K", "Full HD", "500mAh", "4000mAh",
            "2.5 GHz", "3.2 GHz", "50 watts", "15 inches"]
    for _ in range(600):
        t = random.choice(templates_spec)
        augmented.append(t.format(
            random.choice(parts), random.choice(parts), random.choice(vals)
        ))

    # Factual number templates
    for n in range(1, 300):
        augmented.append(f"The total count is {n * random.randint(1, 100)}.")
        augmented.append(f"The file contains {n * random.randint(2, 50)} records.")

    all_neutral = base + augmented
    random.shuffle(all_neutral)

    # Deduplicate and trim
    seen = set()
    unique = []
    for s in all_neutral:
        key = s.lower().strip()
        if key not in seen and len(key) > 10:
            seen.add(key)
            unique.append(s)

    print(f"  Generated {len(unique)} unique neutral sentences.")

    # If still not enough, repeat
    while len(unique) < target:
        unique += unique
    return unique[:target]


def create_explicit_positive():
    """Extra explicit positive sentences to supplement movie reviews."""
    return [
        "This is absolutely the best product I have ever purchased.",
        "I am extremely satisfied with this purchase.",
        "Highly recommend this to everyone, it exceeded my expectations.",
        "Outstanding quality and fast delivery, very happy with this.",
        "Excellent customer service and a great product overall.",
        "This product changed my life, I love it so much.",
        "Amazing experience from start to finish, five stars.",
        "Wonderful quality and the design is beautiful.",
        "I am so impressed with this, it works perfectly.",
        "Best purchase I made this year, absolutely fantastic.",
        "The quality is superb and the price is very reasonable.",
        "I love this product, it is exactly what I needed.",
        "Incredible value for money, highly satisfied.",
        "This is perfect, I couldn't be happier with it.",
        "Fantastic product, works better than advertised.",
        "Great experience, will definitely buy again.",
        "Super happy with this purchase, everything is perfect.",
        "Very pleased with the quality and fast shipping.",
        "This exceeded all my expectations, amazing product.",
        "Delightful experience, I recommend this to all my friends.",
    ] * 100  # repeat to get enough


def create_explicit_negative():
    """Extra explicit negative sentences to supplement movie reviews."""
    return [
        "This is the worst product I have ever bought.",
        "Completely disappointed with this purchase.",
        "Terrible quality, broke after one day of use.",
        "Do not buy this, it is a waste of money.",
        "Awful customer service, they refused to help me.",
        "This product is useless and doesn't work at all.",
        "Very dissatisfied with this purchase, total scam.",
        "Horrible experience, I want my money back.",
        "The worst purchase I have ever made in my life.",
        "Extremely poor quality, fell apart immediately.",
        "This is garbage, complete waste of money.",
        "Disgusting product, I am very angry about this.",
        "Never buying from this store again, terrible service.",
        "Broken on arrival, packaging was damaged.",
        "The item stopped working after a week, very unhappy.",
        "This is the biggest disappointment I have experienced.",
        "Poorly made and cheaply constructed, avoid this.",
        "Frustrating experience, the product did not work.",
        "I regret buying this, do not waste your money.",
        "Disgraceful quality and terrible customer support.",
    ] * 100


def main():
    print("\n" + "=" * 60)
    print("  SentiVision AI — 3-Class Dataset Generator")
    print("=" * 60)

    # Load NLTK movie reviews
    pos_texts, neg_texts = load_movie_reviews()

    # Supplement with explicit sentences
    pos_texts += create_explicit_positive()
    neg_texts += create_explicit_negative()

    # Shuffle
    random.shuffle(pos_texts)
    random.shuffle(neg_texts)

    # Augment to target
    pos_texts = augment_to_target(pos_texts, TARGET_PER_CLASS, "Positive")
    neg_texts = augment_to_target(neg_texts, TARGET_PER_CLASS, "Negative")
    neu_texts = build_neutral_texts(TARGET_PER_CLASS)

    print(f"\n  Final class sizes:")
    print(f"    Positive:  {len(pos_texts)}")
    print(f"    Neutral:   {len(neu_texts)}")
    print(f"    Negative:  {len(neg_texts)}")

    # Build DataFrame — labels: 0=Negative, 1=Neutral, 2=Positive
    records = (
        [(t, 2) for t in pos_texts] +
        [(t, 1) for t in neu_texts] +
        [(t, 0) for t in neg_texts]
    )
    random.shuffle(records)

    df = pd.DataFrame(records, columns=['text', 'sentiment'])
    df['text'] = df['text'].astype(str).str.strip()
    df = df[df['text'].str.len() > 5].reset_index(drop=True)

    # Save
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    print(f"\n  Dataset saved: {OUTPUT_PATH}")
    print(f"  Total records: {len(df)}")
    print(f"\n  Distribution:")
    labels = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    for code, name in labels.items():
        count = (df['sentiment'] == code).sum()
        pct = count / len(df) * 100
        print(f"    {name}: {count} ({pct:.1f}%)")
    print()


if __name__ == '__main__':
    main()
