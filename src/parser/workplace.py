# -*- coding: utf-8 -*-

import os
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Workplace:
	def __init__(self, event):
		if ('queryStringParameters' in event and 'hub.challenge' in event['queryStringParameters']):

			self.validate = event['queryStringParameters']['hub.challenge']
		
		if 'entry' in event and 'messaging' in event['entry'][0]:

			message = event['entry'][0]['messaging'][0]
			self.message_id = message['message']['mid']
			self.recipient_id = message['sender']['id']
			self.text = message['message']['text']

	# Envia uma mensagem no slack como o BOT
	def send_message(self, message):
		
		ret = { "recipient_id": self.recipient_id, "message_id": self.message_id}
		
		return ret
