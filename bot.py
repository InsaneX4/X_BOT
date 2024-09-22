import tweepy
import re
from datetime import datetime
import pytz
from pytz import timezone
import os

# Twitter API credentials from environment variables
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Authenticate to Twitter
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Function to extract time from tweet text
def extract_time_from_text(text):
    match = re.search(r'(\d{1,2})(?:\s)?(am|pm)\s?(pst|est|cst|gmt|ist|utc|etc)?', text, re.IGNORECASE)
    if match:
        time_str = match.group(1) + " " + match.group(2)  # Example: "9 pm"
        tz_str = match.group(3).upper() if match.group(3) else "PST"
        return time_str, tz_str
    return None, None

# Function to convert the extracted time to local time
def convert_time_to_local(time_str, tz_str, local_tz_str):
    time_obj = datetime.strptime(time_str, '%I %p')  # Parse as 12-hour format (e.g., "9 PM")
    from_tz = timezone(tz_str.upper())
    to_tz = timezone(local_tz_str)
    now = datetime.now(from_tz)
    time_with_date = now.replace(hour=time_obj.hour, minute=0, second=0, microsecond=0)
    local_time = time_with_date.astimezone(to_tz)
    return local_time

# Function to check mentions and respond
def check_mentions():
    mentions = api.mentions_timeline()
    for mention in mentions:
        tweet_text = mention.text
        local_tz_str = 'Asia/Kolkata'
        time_str, tz_str = extract_time_from_text(tweet_text)

        if time_str and tz_str:
            local_time = convert_time_to_local(time_str, tz_str, local_tz_str)
            response_text = f"@{mention.user.screen_name} The event will happen at {local_time.strftime('%I:%M %p %Z')} in your local time."
            api.update_status(response_text, in_reply_to_status_id=mention.id)
        else:
            api.update_status(f"@{mention.user.screen_name} Couldn't find a time in your tweet.", in_reply_to_status_id=mention.id)

# Run the check_mentions function in a loop or on a schedule
if __name__ == "__main__":
    check_mentions()
