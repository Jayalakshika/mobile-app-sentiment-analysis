import pandas as pd
import random
import numpy as np
from textblob import TextBlob
from pymongo import MongoClient

# ================= CONFIG =================
CSV_FILE = "mobile_app_reviews.csv"

MONGO_URI = "mongodb+srv://appuser:apppass@cluster0.yrcmpgy.mongodb.net/?appName=Cluster0"

# ================= MONGODB CONNECTION =================
client = MongoClient(MONGO_URI)
db = client["appPulseDB"]
collection = db["app_reviews"]

# ================= LOAD CSV =================
df = pd.read_csv(CSV_FILE)

# Clean column names (safe practice)
df.columns = df.columns.str.strip().str.lower()

print("✅ Mobile App Reviews CSV Loaded")

# ================= CREATE RATINGS (SAFE FIX) =================
# If rating column does not exist, create it
if "rating" not in df.columns:
    df["rating"] = np.random.choice([1, 2, 3, 4, 5], size=len(df))

# ================= REVIEW GENERATION =================
def generate_review(rating):
    rating = float(rating)
    if rating >= 4:
        return random.choice([
            "Excellent app! Very smooth and useful.",
            "Great user interface and performance.",
            "Highly recommended mobile application."
        ])
    elif rating >= 3:
        return random.choice([
            "Average app, works fine most of the time.",
            "Decent features but needs improvement.",
            "Okay app for basic usage."
        ])
    else:
        return random.choice([
            "Very buggy and slow.",
            "Poor user experience and frequent crashes.",
            "Not satisfied with this app."
        ])

df["reviewtext"] = df["rating"].apply(generate_review)

# ================= SENTIMENT ANALYSIS =================
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

df["sentiment"], df["score"] = zip(*df["reviewtext"].apply(analyze_sentiment))

# ================= STORE IN MONGODB =================
collection.delete_many({})
collection.insert_many(df.to_dict("records"))

print("✅ Mobile App Reviews Stored Successfully in MongoDB")
