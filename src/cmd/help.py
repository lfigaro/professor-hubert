# -*- coding: utf-8 -*-

import ConfigParser
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Help:

	def __init__(self, help, message):
		self.text = message

	def execute(self):
		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		ret = config.get('command-help', 'help-text')

		return ret