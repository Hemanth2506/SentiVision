import os
import random
import pandas as pd

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'reviews.csv')

# Base neutral sentences from original dataset generator that are high quality
BASE_NEUTRAL_SENTENCES = [
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
    "The Amazon River is the largest river by discharge in the world."
]

# Sentiment keywords that shouldn't appear in neutral statements to prevent training bleed
SENTIMENT_KEYWORDS = {
    "amazing", "worst", "waste", "love", "terrible", "happy", "hate", "disappointed",
    "awful", "bad", "great", "excellent", "superb", "perfect", "horrible", "glad",
    "useless", "scam", "cheap", "refund", "poor", "outstanding", "fantastic", "satisfy",
    "satisfied", "wonderful", "incredible", "disgraceful", "regret", "frustrated",
    "annoyed", "useless", "broken", "fail", "failed", "rude", "delayed", "slow"
}

def clean_and_generate_neutrals(target_count):
    # Generative lists
    # 1. Specs
    spec_subjects = ["The laptop", "The tablet", "The desktop", "The smartphone", "The camera", "The monitor", "The router", "The keyboard", "The headphones", "The speaker", "The smartwatch", "The printer", "The charger", "The drive", "The processor", "The card"]
    spec_verbs = ["has", "features", "includes", "supports", "comes with", "is equipped with", "provides", "delivers"]
    spec_details = [
        "16GB RAM and a 512GB SSD", "a 6.5 inch display", "USB-C fast charging", "a battery capacity of 4000 mAh",
        "a resolution of 1920 by 1080", "a clock speed of 3.2 GHz", "256 gigabytes of internal storage", "two color options",
        "a weight of approximately 500 grams", "a 12-megapixel resolution", "a refresh rate of 120 Hz", "dual-band WiFi",
        "an output of 20 watts", "a fuel capacity of 60 liters", "a frequency range of 20 to 20000 Hz", "a minimum of 4 GB of RAM",
        "a read speed of 550 MB per second", "a focal length of 50mm", "an output of 650 watts", "a cable length of 1.8 meters",
        "dimensions of 30 by 20 by 10 centimeters", "a voltage of 110 to 240 volts", "paper sizes up to A3", "8 GB of dedicated VRAM",
        "up to 32 GB of RAM", "a battery life of 10 hours", "water resistance up to 50 meters", "a quad-core CPU architecture"
    ]

    # 2. Meetings
    meeting_subjects = ["The meeting", "The presentation", "The event", "The seminar", "The kickoff session", "The board meeting", "The interview", "The training workshop", "The sync call", "The lecture", "The exam", "The review session"]
    meeting_verbs = ["is scheduled for", "begins at", "starts at", "takes place on", "is planned for", "is confirmed for", "has been rescheduled to"]
    meeting_details = [
        "Monday morning", "10 AM tomorrow", "3 PM on Thursday", "next Friday at noon", "Wednesday at 9:30 AM",
        "2 PM in Room 305", "9 AM in the main conference hall", "noon in the boardroom", "5 PM this evening",
        "the first Tuesday of the month", "the end of the fiscal quarter", "Friday morning at 11 AM",
        "Tuesday and Thursday at 1:30 PM", "next Monday at 8 AM", "Room 402 this afternoon", "10 AM sharp"
    ]

    # 3. Logistics
    logistics_subjects = ["The package", "The item", "The shipment", "The delivery", "The box", "The product", "The order", "The parcel", "The invoice", "The receipt"]
    logistics_verbs = ["arrived", "was delivered", "was shipped", "is in transit", "was dispatched", "was sent"]
    logistics_details = [
        "yesterday morning", "via standard ground carrier", "containing two separate items", "with a charger and a user manual",
        "three days after the order date", "to the front door at 2 PM", "with the tracking number emailed to you",
        "in a cardboard box", "to the local post office", "with a 30-day return window", "to the shipping address on file",
        "with standard packaging", "by the expected date", "containing the items listed on the invoice", "via express air courier",
        "within three business days"
    ]

    neutral_pool = list(BASE_NEUTRAL_SENTENCES)

    # Combinatorial generation
    random.seed(42)
    
    # Specs
    for sub in spec_subjects:
        for verb in spec_verbs:
            for detail in spec_details:
                neutral_pool.append(f"{sub} {verb} {detail}.")

    # Meetings
    for sub in meeting_subjects:
        for verb in meeting_verbs:
            for detail in meeting_details:
                neutral_pool.append(f"{sub} {verb} {detail}.")

    # Logistics
    for sub in logistics_subjects:
        for verb in logistics_verbs:
            for detail in logistics_details:
                neutral_pool.append(f"{sub} {verb} {detail}.")

    # Clean and filter
    cleaned_pool = []
    seen = set()
    for s in neutral_pool:
        # Check sentiment words
        words = s.lower().replace('.', '').replace(',', '').split()
        if any(w in SENTIMENT_KEYWORDS for w in words):
            continue
        normalized = s.strip()
        if normalized.lower() not in seen and len(normalized) > 10:
            seen.add(normalized.lower())
            cleaned_pool.append(normalized)

    random.shuffle(cleaned_pool)
    print(f"Generated a pool of {len(cleaned_pool)} unique, verified opinion-free neutral sentences.")
    return cleaned_pool[:target_count]

def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Please make sure you have downloaded it first.")
        return

    # Load existing dataset
    df = pd.read_csv(DATASET_PATH, encoding='utf-8')
    print("=== Dataset Distribution BEFORE Rebalancing ===")
    label_names = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    for code in [0, 1, 2]:
        count = (df['sentiment'] == code).sum()
        pct = count / len(df) * 100
        print(f"  {label_names[code]} (class {code}): {count} ({pct:.1f}%)")

    # Filter out class 1 (Neutral) and sample classes 0 & 2
    pos_df = df[df['sentiment'] == 2]
    neg_df = df[df['sentiment'] == 0]

    # Sample 2,000 for Positive and Negative
    pos_sampled = pos_df.sample(n=2000, random_state=42)
    neg_sampled = neg_df.sample(n=2000, random_state=42)

    # Generate 2,000 high-quality neutral reviews
    neutral_texts = clean_and_generate_neutrals(2000)
    neutral_df = pd.DataFrame({
        'text': neutral_texts,
        'sentiment': [1] * 2000
    })

    # Combine
    rebalanced_df = pd.concat([pos_sampled, neg_sampled, neutral_df]).sample(frac=1, random_state=42).reset_index(drop=True)
    rebalanced_df['text'] = rebalanced_df['text'].astype(str).str.strip()

    # Save
    rebalanced_df.to_csv(DATASET_PATH, index=False, encoding='utf-8')
    print("\n=== Dataset Distribution AFTER Rebalancing ===")
    for code in [0, 1, 2]:
        count = (rebalanced_df['sentiment'] == code).sum()
        pct = count / len(rebalanced_df) * 100
        print(f"  {label_names[code]} (class {code}): {count} ({pct:.1f}%)")
    print(f"\nSaved {len(rebalanced_df)} rebalanced reviews to {DATASET_PATH}")

if __name__ == '__main__':
    main()
