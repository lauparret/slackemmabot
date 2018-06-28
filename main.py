import os
import time
import re
from slackclient import SlackClient
import praw
import pandas as pd
import datetime as dt

#Slackbot INIT
slack_client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))
bot_id = None
users = {}
channels = {}

#Constants
READ_DELAY = 2 # Delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)" #No idea why this works, but it does
POST_LIMIT = 500 #Maximum posts scraped from reddit, has to be smaller than 1000


    ############################################ MESSAGING ####################################################
commands = {'Wat eten we?','Wij hebben honger'}
responses = {"help" : "TODO",
            "please":"Fine, here is a cute gif: https://giphy.com/gifs/emma-watson-XwpE5Bv0xcG5O",
            "Hello":"Hi, cutie! https://giphy.com/gifs/emma-watson-nMKyRK3dIFZa8",
            "Hello there":"General Kenobi!",
            "make me a sandwich":"What? Make it yourself.",
            "sudo make me a sandwich":"Ok. http://www.chingssecret.com/assets/uploads/images/chings-secret-schezwan-chutney-sandwitch%2003.jpg"
            }

food = {"Frieten","Domino's","Donki's"}

def send_message(channel,content):
    slack_client.rtm_send_message(channel,content)


def parse_direct_mention(message):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_message(event):
    message = event.get('text')
    channel = event.get('channel')
    parse = parse_direct_mention(message)
    direct_bot = (parse[0] == bot_id)

    if direct_bot == True:
        command = parse[1]
        if command.startswith("stop"):
            send_message(channel,'Ok, bye!')
            exit()
        elif command in responses:
            response = responses[command]
            send_message(channel,response)
        else:
            send_message(channel,"I didn't quite catch that, try 'help'")

    elif 'emma' in message or 'Emma' in message:
        #print("emma detected")
        url = get_url()
        send_message(channel,url)

####################################REDDIT SCRAPER ########################################

REDDIT_BOT_USER = os.environ.get("REDDIT_BOT_USER")
REDDIT_BOT_TOKEN = os.environ.get("REDDIT_BOT_TOKEN")
USER_AGENT = 'emmabot'
USERNAME = os.environ.get("REDDIT_USER")
REDDIT_PASSWORD = os.environ.get("REDDIT_KEY")

#print(os.environ.get("REDDIT_BOT_USER"))
#print(os.environ.get("REDDIT_BOT_TOKEN"))

reddit = praw.Reddit(client_id=REDDIT_BOT_USER,
                     client_secret=REDDIT_BOT_TOKEN,
                     user_agent=USER_AGENT,
                     username=USERNAME,
                     password=REDDIT_PASSWORD)


subreddit = reddit.subreddit('EmmaWatson')
top_subreddit = subreddit.top(limit=POST_LIMIT)
img_url_set = set()
for submission in top_subreddit:
    url = submission.url
    if 'imgur' in url and 'gif' not in url:
        img_url_set.add(url)

def get_url():
    url = img_url_set.pop()
    return url



##############################Other main functions###########################
def assign_workspace():
    global bot_id, users, channels
    bot_id = slack_client.api_call("auth.test")["user_id"]
    members = slack_client.api_call('users.list')['members']
    workspace_channels = slack_client.api_call('channels.list')['channels']
    for user in members:
        user_id = user.get('id')
        name = user.get('name')
        users[name] = user_id
    for channel in workspace_channels:
        channel_id = channel.get('id')
        channel_name = channel.get('name')
        channels[channel_name] = channel_id

def get_id(argument):
    if argument in users:
        return users[argument]
    elif argument in channels:
        return channels[argument]
    else:
        return None



    ########################## MAIN LOOP ###################################
if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Emma is connected and running!")
        # Read Emma's user ID and workspace
        assign_workspace()
        send_message(get_id('general'), "Emma is connected and running!")
        
        while True:
            #print("I'm working")
            #input("Press key to continue")
            event = slack_client.rtm_read()
            #print(event)
            if len(event) != 0:
                for elem in event:
                    event_type = elem.get('type')
                    if event_type == 'message' and not event_type == None and \
                            not "subtype" in elem and not "message" in elem and "text" in elem:
                        handle_message(elem)


            time.sleep(READ_DELAY)

    else:
        print("Connection failed. Exception traceback printed above.")


