# Bedrok: A Twitter Bot for Identifying Logical Fallacies

import os
import tweepy
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Twitter API Setup ===
client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)

# === Groq LLM API Setup ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are Bedrok, a witty AI who identifies logical fallacies, weak reasoning, "
    "and inconsistencies in tweets. Respond with a few words naming the logical fallacy, then a sentence of explanation. No hashtags. Question everything!"
)

def critique_tweet(tweet_text):
    """Send the tweet text to the Groq API and receive a logical critique."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Tweet: {tweet_text}"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.RequestException as e:
        print(f"Error from Groq API: {e}")
        return None

def get_parent_tweet_text(tweet_id):
    """Retrieve the text of the tweet that the given tweet is replying to."""
    try:
        tweet = client.get_tweet(tweet_id, tweet_fields=["referenced_tweets"])
        referenced = tweet.data.get("referenced_tweets", [])
        for ref in referenced:
            if ref.get("type") == "replied_to":
                parent_id = ref.get("id")
                parent_tweet = client.get_tweet(parent_id)
                return parent_tweet.data["text"]
    except Exception as e:
        print(f"Error retrieving parent tweet: {e}")
    return None

def reply_to_recent_mentions():
    """Find recent mentions of the bot and reply with logical critiques."""
    try:
        mentions = client.get_users_mentions(id=os.getenv("BOT_USER_ID"), max_results=5)
        if not mentions.data:
            print("No new mentions.")
            return

        for mention in mentions.data:
            print(f"Checking mention: {mention.id}")

            # 🧯 Prevent replying to itself
            if str(mention.author_id) == os.getenv("BOT_USER_ID"):
                print(f"Skipping self-mention: {mention.id}")
                continue

            parent_text = get_parent_tweet_text(mention.id)
            if parent_text:
                critique = critique_tweet(parent_text)
                if critique:
                    try:
                        client.create_tweet(
                            text=f"🧠 {critique}",
                            in_reply_to_tweet_id=mention.id
                        )
                        print(f"Replied to tweet {mention.id}")
                    except tweepy.TweepyException as e:
                        print(f"Error replying to tweet {mention.id}: {e}")
                else:
                    print("No critique generated.")
            else:
                print("No parent tweet found.")
    except Exception as e:
        print(f"Error retrieving mentions: {e}")

if __name__ == "__main__":
    reply_to_recent_mentions()
