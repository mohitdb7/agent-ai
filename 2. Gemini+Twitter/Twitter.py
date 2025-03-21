#%% Import libraries
import tweepy
import json

#%% Twitter post function
def post_on_twitter(tweet_text):
    try:
        #Get twitter keys
        with open('../Keys/twitter_keys.txt') as json_file:
            TWITTER_KEYS = json.load(json_file)

        # Assign API keys
        API_KEY = TWITTER_KEYS["api_key"]
        API_SECRET = TWITTER_KEYS["api_secret"]
        ACCESS_TOKEN = TWITTER_KEYS["access_token"]
        ACCESS_SECRET = TWITTER_KEYS["access_token_secret"]
        BEARER_TOKEN = TWITTER_KEYS["bearer_token"]  # Needed for API v2
        CLIENT_TOKEN = TWITTER_KEYS["client_token"]  # Needed for API v2
        CLIENT_SECRET = TWITTER_KEYS["client_secret"]  # Needed for API v2

        # TWitter client - Authenticate using API v2
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )

        # Post a tweet
        response = client.create_tweet(text=tweet_text)
        print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"Error: {e}")
