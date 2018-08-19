import os
import time
import re
from slackclient import SlackClient
import praw
import pandas as pd
import datetime as dt
import schedule

# Slackbot INIT
slack_client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))
bot_id = None
users = {}
channels = {}

# Constants
READ_DELAY = 2  # Delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"  # No idea why this works, but it does


############################################ MESSAGING ####################################################
commands = {'Wat eten we?', 'Wij hebben honger'}
responses = {"help": "I listen to: 'please', 'Hello there', 'mokke', 'go wild' and some other stuff",
             "please": "Fine, here is a cute gif: https://giphy.com/gifs/emma-watson-XwpE5Bv0xcG5O",
             "Hello": "Hi, cutie! https://giphy.com/gifs/emma-watson-nMKyRK3dIFZa8",
             "Hello there": "General Kenobi!",
             "make me a sandwich": "What? Make it yourself.",
             "sudo make me a sandwich": "Ok. http://www.chingssecret.com/assets/uploads/images/chings-secret-schezwan-chutney-sandwitch%2003.jpg"
             }

food = {"Frieten", "Domino's", "Donki's"}

class message:
    def __init__(self,channel=None, content=None):
        self.set_content(content)
        self.set_channel(channel)

    def send(self):
        if self.content != None and self.channel_id != None:
             slack_client.rtm_send_message(self.channel_id,self.content)
        else:
             print('Message not sent, no content or id specified')

    def set_content(self,content):
        self.content = content
    def set_channel(self,channel):
        id = get_id(channel)
        if id != None:
            self.channel_id = id
        else:
            self.channel_id = channel

    def clear(self):
        self.content, self.channel_id = None, None

############# Mention handling ##############
def parse_direct_mention(message):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_message_event(event):
    content = event.get('text')
    channel = event.get('channel')
    parse = parse_direct_mention(content)
    direct_bot = (parse[0] == bot_id)
    reply = message(channel)

    if direct_bot == True:
        command = parse[1]
        if command.startswith("stop"):
            reply.set_content('Ok, bye!')
            reply.send()
            exit()
        elif command in responses:
            reply.set_content(responses[command])

        elif command.startswith("send nudes"):
            message(channel,
                 "https://78.media.tumblr.com/a671be346722c876dd44925912bc51d6/tumblr_inline_osgqtm7Yxx1rifr4k_250.gif").send()
            reply.set_content("Excuse me?")

        elif command.startswith("mokke"):
            reply.set_content(gentleman.get_url())
        elif command.startswith("go wild") or command.startswith("let's go on safari"):
            reply.set_content(gonewild.get_url())

        else:
            reply.set_content("I didn't quite catch that, try 'help'")

    elif 'emma' in content or 'Emma' in content:
        #print("emma detected")
        reply.set_content(emma.get_url())


    if reply.content!= None:
        reply.send()



####################################REDDIT SCRAPER ########################################

REDDIT_BOT_USER = os.environ.get("REDDIT_BOT_USER")
REDDIT_BOT_TOKEN = os.environ.get("REDDIT_BOT_TOKEN")
USER_AGENT = 'emmabot'
USERNAME = os.environ.get("REDDIT_USER")
REDDIT_PASSWORD = os.environ.get("REDDIT_KEY")

# print(os.environ.get("REDDIT_BOT_USER"))
# print(os.environ.get("REDDIT_BOT_TOKEN"))

reddit = praw.Reddit(client_id=REDDIT_BOT_USER,
                     client_secret=REDDIT_BOT_TOKEN,
                     user_agent=USER_AGENT,
                     username=USERNAME,
                     password=REDDIT_PASSWORD)


class redditurl:
    def __init__(self,subreddit,type='img',postLimit=500):
        self.subredditName = subreddit
        self.subreddit = reddit.subreddit(self.subredditName)
        self.limit = postLimit

        all_submissions = self.get_top_submissions()
        if type == 'img':
            self.urlset = self.submission_filter_imgur(all_submissions)
        elif type == 'gif':
            pass

    def get_top_submissions(self):
        return self.subreddit.top(limit=self.limit)

    def submission_filter_imgur(self,all_submissions,type='img'):
        filtered = set()
        for submission in all_submissions:
            url = submission.url
            if type =='img' and 'imgur' in url and 'gif' not in url:
                filtered.add(url)
            elif type =='gif' and 'gif' in url:
                filtered.add(url)
        return filtered
        # if type == 'img':
        #     return set(filter(lambda submission: 'imgur' in submission.url and 'gif' not in submission.url, all_submissions))

    def get_url(self):
        url = self.urlset.pop()
        return url

emma = redditurl('EmmaWatson',postLimit=10)
gentleman = redditurl('gentlemanboners',postLimit=10)
gonewild = redditurl('gonewild',postLimit=10)

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


def bonjour():
    url = gentleman.get_url()
    message('testchannel', url).send()
    time.sleep(1)
    message('testchannel', "Bonjour!").send()


########################## MAIN LOOP ###################################


if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Emma is connected and running!")
        # Read Emma's user ID and workspace
        assign_workspace()

        message('testchannel', "Version 2.0 is connected and running!").send()
        schedule.every().day.at("08:00").do(bonjour)

        while True:
            # print("I'm working")
            # input("Press key to continue")
            schedule.run_pending()
            event = slack_client.rtm_read()
            # print(event)
            if len(event) != 0:
                for elem in event:
                    event_type = elem.get('type')
                    if event_type == 'message' and not event_type == None and \
                            not "subtype" in elem and not "message" in elem and "text" in elem:
                        handle_message_event(elem)

            time.sleep(READ_DELAY)

    else:
        print("Connection failed. Exception traceback printed above.")



            ####heroku run -a emmabot123456789 python main.py
            ####heroku ps:scale worker=1 -a emmabot123456789
