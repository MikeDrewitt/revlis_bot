#!/usr/bin/python
import os
import time
import json
import time
import datetime

from slackclient import SlackClient
from pprint import pprint

BOT_NAME = 'silver'
DATABASE = '../db/db.json'

slack_client = SlackClient('xoxp-23584478294-23583487255-94654266630-563d319952ec7a47e0d8b25b38d534de')
BOT_ID = 'U2D8VMVQS'

# constants
AT_BOT = "<@" + BOT_ID + ">"


def is_int(val):
    '''
        Helper fucntion to determain whether or not a string is a number.
    '''
    try:
        if val.isdigit():
            #print("Val is true: " + val)
            return True
    except AttributeError:
        #print("Val is false: " + val)
        return False

def slack_commands_list(command, channel):
    response = "Not sure what you mean. Try again later."

    #This is going to hold the room by updating the json object at paramerterized time and day
    if command.startswith("hullo"):
        slack_client.api_call("chat.postMessage", channel=channel, text="I LIVE!", as_user=True)
    else:
        slack_client.api_call("chat.postMessage", channel=channel, text="No command found.", as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None if there is no messages being sent,
        returns true, the chat message, the channel, and the user if the message
        was directed at the bot, and false with the rest of the return values if it
        is just a message.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return True, output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
            if output and 'text' in output: 
               # return text with no @ mention of the bot
               return False, output['text'].lower(), output['channel'], output['user']

    return None, None, None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Silver connected and running!")

        while True:

            at_bot, command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                if at_bot:
                    slack_commands_list(command, channel)
               
                else:
                    print ('command: ' + command + ', user: ' + user)

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
