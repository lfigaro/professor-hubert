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
import sys
from parser.slack import Slack
from parser.workplace import Workplace

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
	logger.info('event: ' + json.dumps(event))

	# Get from POST or GET requests
	if 'body' in event and \
	   event['body'] is not None:
		event = json.loads(event['body'])
		logger.info('event: ' + json.dumps(event))

	elif 'queryStringParameters' in event and \
	   event['queryStringParameters'] is not None:
		event = event['queryStringParameters']
		logger.info('event: ' + str(event))

	# Execute cron jobs
	if 'source' in event and \
	   event['source'] == 'cron' and \
	   'action' in event:
		ghrepo = None
		if 'squad-repo' in event:
			ghrepo = find_repo(event.pop('squad-repo'))

		class_ = getattr(importlib.import_module("jobs." + event['action']), event['action'].capitalize())
		job = class_(repo.Repo(ghrepo), event)
		job.execute()

		ret = get_return(True, 'job ' + event['action'] + ' executed')
	
	# Execute html requests
	elif 'source' in event and \
	   event.pop('source') == 'html' and \
	   'action' in event and \
	   'squad-repo' in event:

		ghrepo = find_repo(event.pop('squad-repo'))
		functionAttr = getattr(repo.Repo(ghrepo), event.pop('action'))
		jsonr = functionAttr(**event)

		ret = get_return(True, jsonr)

	# Execute BOT commands
	else:
		# Get the right parser
		parser = find_parser(event)

		if parser is not None:
			if hasattr(parser, 'validate'):
				ret = get_return(True, parser.validate)
				return ret

			if hasattr(parser, 'text'):
				ghrepo = find_repo(parser.text)
				if ghrepo is None and hasattr(parser, 'channel_name'):
					ghrepo = parser.channel_name

				logger.info('ghrepo: {}'.format(ghrepo))
				command = find_command(parser.text, ghrepo)
				msg = command.execute()
				ret = get_return(True, parser.send_message(msg))

			else:
				ret = get_return(False, 'invalid command')

		else:
			ret = get_return(False, 'invalid parser')

	return ret

def find_parser(event):
	parser = None

	if 'token' in event and \
	   event['token'] == os.environ['sl_token_src']:
		parser = Slack(event)

	if ('queryStringParameters' in event and \
	   'hub.verify_token' in event['queryStringParameters'] and \
	   event['queryStringParameters']['hub.verify_token'] == os.environ['wp_token_src']) or \
	   ('object' in event and event['object']=='page'):
		parser = Workplace(event)

	return parser

# Identify if the message contains the command
def find_command(message, ghrepo):
	config = ConfigParser.RawConfigParser()
	config.read('command.cfg')
	commands = config.items('commands')

	command = None
	for key, value in commands:
		ret = re.search(r"{}".format(key), message)
		
		if (ret is not None):
			class_ = getattr(importlib.import_module("cmd." + value), value.capitalize())
			command = class_(repo.Repo(ghrepo), message)
			logger.info('command: ' + value)

			find_command_arguments(message, command, value)

	return command

def find_command_arguments(message, command, commandName):
	try:
		#This exists to maintain the keys capitalized
		config = ConfigParser.ConfigParser()
		config.optionxform = str
		config.read('command.cfg')
		commands = config.items('command-' + commandName)

		arguments = None
		for key, value in commands:
			ret = re.search(r"{}".format(key), message)
			
			if (ret is not None):
				argument = ret.group('value')
				setattr(command, value, argument)
				logger.info('argument: %s, value: %s' % (value, argument))
	except:
		logger.info('argument: Error returning arguments.')

# Identify if the message contains the github repo
def find_repo(message):
	ret = None

	if message is not None:
		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		repo_regex = config.get('github', 'repo-regex')
		matchObj = re.search(repo_regex, message, re.M|re.I)
		
		if matchObj:
		   ret = matchObj.group()

	return ret

# Format the return message
def get_return(success, message):
	if success:
		code = 200
	else:
		code = 500

	ret = {
		"statusCode": code,
		"isBase64Encoded": False,
		"headers": {
			"Content-Type": "application/json",
			"Access-Control-Allow-Origin": "*"
		}, 
		'body': json.dumps(message)
	}

	logger.info('return: ' + json.dumps(ret))

	return ret

# To execute by command line
if __name__ == "__main__":
	args = ''
	for index in range(len(sys.argv)):
		if index > 0:
			args += sys.argv[index] + ' '

	handler (json.loads(args), None)