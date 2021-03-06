import os
import time
import re
from slackclient import SlackClient
import praw
# import pandas as pd
import datetime as dt
import schedule
import random
#import requests
# Slackbot INIT
slack_client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))
bot_id = None
users = {}
channels = {}

# Constants
READ_DELAY = 2  # Delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"  # No idea why this works, but it does


############################################ MESSAGING ####################################################
help_string = "*A short user's guide to Emma:* \n" \
       "> 'please' : My weakness is polite guys... \n" \
       "> 'Hello' : Or you can just say 'Hi' if you want \n" \
       "> 'Make me a sandwich' : You'll have to ask that very kindly \n" \
       "> 'Emma' : No need to direct mention me, I listen to my name anywhere, anytime... \n" \
       "> 'Wat eten we?' : I make the difficult choices. \n" \
       "> 'mokke' : Only the finest eye candy of the classiest nature can be found here, as beauty is superior to seduction. \n" \
       "> 'ros' or 'redhead' : An SFW image for people who appreciate the beauty of those with red hair. \n" \
       "> 'sexy' : A sexy, well-composed, and artistic image that is as beautiful as it is erotic. \n" \
       "> 'go wild' or 'let's go on safari' : For those who like to go on an adventure. (All posts redirected to klachten_p_en_o) \n" \
       "> 'go wild gif': ~For those who are REALLY in for a ride. Maybe you should search for this on _other_ sites~ discontinued \n" \
       "> 'cat' or 'kitty' : If you need some eyebleach material :cat2:  (All posts redirected to nsfw)  \n" \
       "> '$ sudo poweroff emma' : Stop command; only use case of emergency..."

commands = {'Wat eten we?', 'Wij hebben honger'}
responses = {"help": help_string,
             "please": "Fine, here is a cute gif: https://giphy.com/gifs/emma-watson-XwpE5Bv0xcG5O",
             "Hello": "Hi, cutie! https://giphy.com/gifs/emma-watson-nMKyRK3dIFZa8",
             "Hi": "Hi, cutie! https://giphy.com/gifs/emma-watson-nMKyRK3dIFZa8",
             "Hello there": "General Kenobi!",
             "make me a sandwich": "What? Make it yourself.",
             "sudo make me a sandwich": "Ok. http://www.chingssecret.com/assets/uploads/images/chings-secret-schezwan-chutney-sandwitch%2003.jpg"
             }

food = {"Frieten", "Domino's", "Donki's"}

class message:
    def __init__(self,channel=None, content=None):
        self.set_content(content)
        self.set_channel(channel)
        self.is_nsfw = False

    def send(self):
        if self.content != None and self.channel_id != None:
            if self.is_nsfw == True:
                self.set_channel('klachten_p_en_o')
            self.handshake = slack_client.api_call("chat.postMessage", channel=self.channel_id,text=self.content)
            self.is_sent = self.handshake.get("ok")
            self.timestamp = self.handshake.get("ts")
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
    def set_nsfw(self):
        self.is_nsfw = True
    def clear(self):
        self.content, self.channel_id = None, None

    def self_destruct(self,timer=300):
        time_sent = dt.datetime.now()
        delete_time = time_sent + dt.timedelta(0,timer)
        to_be_deleted[delete_time] = [self.channel_id,self.timestamp]

    def remove(self,channel=None,ts= None):
        if channel == None and ts == None:
            return slack_client.api_call("chat.delete", channel=self.channel_id, ts=self.timestamp)
        else:
            slack_client.api_call("chat.delete", channel=channel, ts=ts)

############# Mention handling ##############
to_be_deleted = {}
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
    user = event.get('user')
    parse = parse_direct_mention(content)
    direct_bot = (parse[0] == bot_id)
    reply = message(channel)
    destruct = False

    if direct_bot == True:
        command = parse[1]
        command = command.lower()
        if command.startswith("$ sudo poweroff emma"):
            reply.set_content('Ok, bye!')
            reply.send()
            exit()
        elif command in responses:
            reply.set_content(responses[command])

        elif command.startswith("send nudes"):
            message(channel,
                 "https://78.media.tumblr.com/a671be346722c876dd44925912bc51d6/tumblr_inline_osgqtm7Yxx1rifr4k_250.gif").send()
            reply.set_content("Excuse me?")
        elif command.startswith("Wat eten we?"):
            choice = random.sample(food,1)
            reply.set_content(choice[0])
        elif command.startswith("mokke"):
            reply.set_content(gentleman.get_url())
            reply.set_nsfw()
        elif command.startswith("make coffee"):
            reply.set_content(make_coffee(user))
        elif command.startswith("ros") or command.startswith("redhead"):
            reply.set_content(ros.get_url())
            reply.set_nsfw()
        elif command.startswith("cat") or command.startswith("kitty"):
            reply.set_content(cats.get_url())
        elif command.startswith("sexy"):
            reply.set_content(sexy.get_url())
            reply.set_nsfw()
        elif command.startswith("go wild gif"):
            message(channel,"This feature has been discontinued, please contact the high king to file a complaint. A cute cat will be sent as compensation").send()
            reply.set_content(cats.get_url())
            reply.set_nsfw()
            destruct = False
        elif command.startswith("lucy"):
            message(channel,"Groetjes van Lucy_Bot").send()
            reply.set_content(lucy.get_url())
            reply.set_nsfw()
            destruct = False
        elif command.startswith("alex") or command.startswith("medusa"):
            reply.set_content(alex.get_url())
            reply.set_nsfw()
            destruct = False
        elif command.startswith("go wild") or command.startswith("let's go on safari"):
            reply.set_content(gonewild.get_url())
            reply.set_nsfw()
            destruct = True

        else:
            reply.set_content("I didn't quite catch that, try 'help'")

    elif 'emma' in content or 'Emma' in content:
        #print("emma detected")
        reply.set_content(emma.get_url())

    if reply.content!= None:
        reply.send()
        if destruct == True:
            reply.self_destruct()

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
        
        all_submissions = self.get_hot_submissions()
        if type == 'img':
            self.urlset = self.submission_filter_imgur(all_submissions)
        elif type == 'gif':
            self.urlset = self.submission_filter_imgur(all_submissions,type)

    def get_top_submissions(self):
        return self.subreddit.top('week',limit=self.limit)

    def get_hot_submissions(self):
        return self.subreddit.hot(limit=self.limit)
       
    def submission_filter_imgur(self,all_submissions,type='img'):
        filtered = set()
        for submission in all_submissions:
            url = submission.url
            if type =='img' and 'imgur' in url and 'gif' not in url:
                filtered.add(url)
            elif type =='gif' and ('gif' in url or 'gfy' in url):
                filtered.add(url)
        return filtered
        # if type == 'img':
        #     return set(filter(lambda submission: 'imgur' in submission.url and 'gif' not in submission.url, all_submissions))

    def get_url(self):
        url = random.sample(self.urlset,1)
        #url = self.urlset.pop()
        return url[0]

emma = redditurl('EmmaWatson')
gentleman = redditurl('gentlemanboners')
gonewild = redditurl('gonewild', postLimit=100)
#gonewildgif = redditurl('gifsgonewild','gif',100)
ros = redditurl('SFWRedHeads',postLimit=400)
cats = redditurl('cats',postLimit=100)
sexy = redditurl('SexyButNotPorn',postLimit=500)
lucy = redditurl('lucypinder',postLimit=100)
alex = redditurl('alexandradaddario',postLimit=500)
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
    message('klachten_p_en_o', url).send()
    time.sleep(1)
    message('klachten_p_en_o', "Bonjour!").send()

def check_selfdestruct():
    copy = to_be_deleted.copy()
    for elem in copy.keys():
        if elem < dt.datetime.now():
            message_to_delete = to_be_deleted[elem]
            channel = message_to_delete[0]
            timestamp = message_to_delete[1]
            message().remove(channel,timestamp)
            del to_be_deleted[elem]

def make_coffee(userid):
    if userid == 'U5A7GT5EZ':
        #requests.post("http://coffeemachine/Coffee")
        return "Making coffee!"
    else:
        return "Sorry, you have no permission to do that."

########################## MAIN LOOP ###################################


if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Emma is connected and running!")
        # Read Emma's user ID and workspace
        assign_workspace()

        message('testchannel', "Version 2.0 is connected and running!").send()
        schedule.every().day.at("08:00").do(bonjour)
        schedule.every(10).seconds.do(check_selfdestruct)

        while True:
            # print("I'm working")
            # input("Press key to continue")
            schedule.run_pending()
            event = slack_client.rtm_read()
            print(event)
            if len(event) != 0:
                for elem in event:
                    event_type = elem.get('type')
                    if event_type == 'message' and not event_type == None and \
                            not "subtype" in elem and not "message" in elem and "text" in elem:
                        handle_message_event(elem)

                    elif elem.get('username') == 'IFTTT':
                        sent_command = elem.get('attachments')[0]
                        sent_content = sent_command.get('pretext')
                        print(sent_content)
                        if sent_content == 'Emma':
                            dummy_text = 'Emma'
                        else:
                            dummy_text = '<@UAZS9KMEU> ' + sent_content
                        print(dummy_text)
                        dummy_message = {'type': 'message', 'user': 'U5A7GT5EZ',
                                          'text': dummy_text, 'team': 'T5A751T1B', 'channel': 'C5A2772EP'}
                        handle_message_event(dummy_message)

            time.sleep(READ_DELAY)

    else:
        print("Connection failed. Exception traceback printed above.")



            ####heroku run -a emmabot123456789 python main.py
            ####heroku ps:scale worker=1 -a emmabot123456789
