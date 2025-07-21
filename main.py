import os
import tweepy
from dotenv import load_dotenv
from your_groq_module import critique_tweet, get_parent_tweet_text  # adjust import as needed

load_dotenv()

client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)

def reply_to_recent_mentions():
    """Find recent mentions of the bot and reply with logical critiques."""
    try:
        mentions = client.get_users_mentions(id=os.getenv("BOT_USER_ID"), max_results=5)
        if not mentions.data:
            print("No new mentions.")
            return

        for mention in mentions.data:
            print(f"Found mention ID: {mention.id} from author ID: {mention.author_id}")
            print(f"Mention text: {mention.text}")

            # Prevent replying to self
            if str(mention.author_id) == os.getenv("BOT_USER_ID"):
                print(f"Skipping self-mention: {mention.id}")
                continue

            parent_text = get_parent_tweet_text(mention.id)
            print(f"Parent tweet text: {parent_text}")

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
