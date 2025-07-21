# test_bedrok_local.py
# Simple script to test Bedrok's reasoning locally without needing Twitter API

import os
from dotenv import load_dotenv
from main import critique_tweet

# Load Groq API key
load_dotenv()

if __name__ == "__main__":
    print("🧪 Bedrok Local Test Mode")
    while True:
        tweet = input("\nEnter a tweet to analyze (or 'q' to quit):\n> ")
        if tweet.strip().lower() == 'q':
            break
        critique = critique_tweet(tweet)
        print("\n🧠 Bedrok's critique:")
        print(critique or "(No response received)")
