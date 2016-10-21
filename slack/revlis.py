#!/usr/bin/python
import os
import time
import json
import time
import datetime

from slackclient import SlackClient
from pprint import pprint

BOT_NAME = 'silver'

CHANNEL_ARRAY = []

SLACK_CLIENT = SlackClient('xoxp-23584478294-23583487255-94654266630-563d319952ec7a47e0d8b25b38d534de')
BOT_ID = 'U2D8VMVQS'
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

def get_bot_channels(slack_client, bot_id):

    channel_list = slack_client.api_call('channels.list')
    group_list = slack_client.api_call('groups.list')

    bot_channels = []

    #print(slack_client.api_call('channels.info', channel="C0VN9R41F"))

    for channel in channel_list['channels']:

        if not channel['is_archived']:
            channel_id = channel['id']

            channel_info = slack_client.api_call('channels.info', channel=channel_id)

            #print(channel_info)

            for member in channel_info['channel']['members']:
                if BOT_ID == member:
                    #print('found him! in ' + channel_info['channel']['name'])
                    bot_channels.append(channel_id)


    for group in group_list['groups']:

        if not group['is_archived']:
            group_id = group['id']
            group_info = slack_client.api_call('groups.info', channel=group_id)

            #print(group_info)

            for member in group_info['group']['members']:
                if BOT_ID == member:
                    #print('found him! in ' + group_info['group']['name'])
                    bot_channels.append(group_id)

    return bot_channels

def slack_commands_list(command, channel):
    global CHANNEL_ARRAY

    response = "Not sure what you mean. Try again later."

    #This is going to hold the room by updating the json object at paramerterized time and day
    if command.startswith("refresh"):
        CHANNEL_ARRAY = get_bot_channels(SLACK_CLIENT, BOT_ID)
        SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text="Channel list has been refreshed!", as_user=True)
    if command.startswith('test'):
        CHANNEL_ARRAY = ['new_array', 'woooooo']
        SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text="testing stuff", as_user=True)
    else:
        SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text="No command found.", as_user=True)

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
                # return true, and all data info after
               output['text'] = output['text'].split(AT_BOT)[1].strip().lower()
               return True, output

            if output and 'text' in output:
               # return false and all data info
               return False, output

    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if SLACK_CLIENT.rtm_connect():
        print("Silver connected and running!")

        CHANNEL_ARRAY = get_bot_channels(SLACK_CLIENT, BOT_ID)

        print(CHANNEL_ARRAY)
  
        while True:

            at_bot, chat_dictionary = parse_slack_output(SLACK_CLIENT.rtm_read())
            
            if at_bot != None:
                channel = chat_dictionary['channel']
                command = chat_dictionary['text']

                if at_bot:
                    slack_commands_list(command, channel)
                else:
                    if channel in CHANNEL_ARRAY:
                        print(command)
            else:
                a = 1

            print(CHANNEL_ARRAY)

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
