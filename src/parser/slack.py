# -*- coding: utf-8 -*-

from slackclient import SlackClient
import os
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Slack:
	sc = SlackClient(os.environ['sl_token'])

	def __init__(self, event):
		if 'subtype' in event['event'] and event['event']['subtype'] == 'bot_message':
			return

		if 'event' in event and 'text' in event['event']:
			self.text = event['event']['text']

		if 'event' in event and 'channel' in event['event']:
			self.channel = event['event']['channel']

			ret = self.sc.api_call(
			  "channels.info",
			  channel=event['event']['channel']
			)

			if ret['ok'] == True:
				self.channel_name = ret['channel']['name']
				logger.info('self.channel_name: ' + self.channel_name)

		if 'challenge' in event:
			self.validate = event['challenge']

	# Envia uma mensagem no slack como o BOT
	def send_message(self, message):
		self.sc.api_call(
		  "chat.postMessage",
		  channel=self.channel,
		  text=message,
		  mrkdwn=True
		)

		return 'message sent in channel ' + self.channel
