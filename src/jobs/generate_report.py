# -*- coding: utf-8 -*-
import os
import json
from cmd.report import Report
from parser.slack import Slack
from slackclient import SlackClient

class Generate_report:

	def __init__(self, repo, event):
		self.event = event
		self.repo = repo

	def execute(self):
		event = self.event

		sc = SlackClient(os.environ['sl_token'])
		ret = sc.api_call(
		  "conversations.list",
		  exclude_archived='true',
		  limit=1000
		)

		repos = self.repo.get_repos()
		for channel in ret['channels']:
			if channel['is_member'] is True:
				if channel['name'] in repos['repos']:
					event['event']={'channel': channel['name']} 
					setattr(self.repo, 'ghrepo', channel['name'])
					parser = Slack(event)
					command = Report(self.repo, '')
					msg = command.execute()
					parser.send_message(msg)
