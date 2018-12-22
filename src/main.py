# -*- coding: utf-8 -*-

import ConfigParser
import re
import sys
import importlib
import repo
import requests
import json
import logging
import os

from parser.slack import Slack
from parser.workplace import Workplace

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info('event: ' + json.dumps(event))


    if 'body' in event and \
       event['body'] is not None:
        event = json.loads(event['body'])
        logger.info('event: ' + json.dumps(event))
    elif 'queryStringParameters' in event and \
       event['queryStringParameters'] is not None:
        event = json.loads(event['queryStringParameters'])
        logger.info('event: ' + str(event))
    # Execute cron jobs
    elif 'source' in event and \
       event['source'] == 'cron' and \
       'action' in event:
        class_ = getattr(importlib.import_module("batch." + event['action']), event['action'].capitalize())
        command = class_(event)
        command.execute()
        return

    parser = None
    if 'token' in event and \
       event['token'] == os.environ['sl_token_src']:
        parser = Slack(event)

    if ('queryStringParameters' in event and \
       'hub.verify_token' in event['queryStringParameters'] and \
       event['queryStringParameters']['hub.verify_token'] == os.environ['wp_token_src']) or \
       ('object' in event and event['object']=='page'):
        parser = Workplace(event)       

    if hasattr(parser, 'validate'):
        ret = {
            "statusCode": 200,
            "isBase64Encoded": False,
            'body': parser.validate
        }
        
        return ret

    if hasattr(parser, 'text'):
        ghrepo = find_repo(parser.text)
        if ghrepo is None and hasattr(parser, 'channel_name'):
            ghrepo = parser.channel_name

        logger.info('ghrepo: ' + ghrepo)

        command = find_command(parser.text, ghrepo)
        msg = command.execute()

        ret = {
            "statusCode": 200,
            "isBase64Encoded": False,
            'body': parser.send_message(msg)
        }

    else:
        ret = {
            "statusCode": 500,
            "isBase64Encoded": False,
            'body': 'invalid command'
        }

    logger.info('return: ' + json.dumps(ret))
    return ret

# Identify if the message contains the command
def find_command(message, ghrepo):
    config = ConfigParser.RawConfigParser()
    config.read('command.cfg')
    commands = config.items('commands')

    command = None
    for key, value in commands:
        ret = re.search(key, message)
        
        if (ret is not None):
            class_ = getattr(importlib.import_module("cmd." + value), value.capitalize())
            command = class_(repo.Repo(ghrepo), message)
            logger.info('command: ' + value)

    return command

# Identify if the message contains the github repo
def find_repo(message):
    ret = None

    config = ConfigParser.RawConfigParser()
    config.read('command.cfg')
    repo_regex = config.get('github', 'repo-regex')
    matchObj = re.search(repo_regex, message, re.M|re.I)
    
    if matchObj:
       ret = matchObj.group()

    return ret

if __name__ == "__main__":
    args = ''
    for index in range(len(sys.argv)):
        if index > 0:
            args += sys.argv[index] + ' '

    handler (json.loads(args), None)
    #handler({"token": os.environ['sl_token_src'], "event": {"channel": "CA16GDSTG", "text": "<@UAEKQ2H1P> " + args } }, None)