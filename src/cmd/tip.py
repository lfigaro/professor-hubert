# -*- coding: utf-8 -*-

import ConfigParser
import random
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Tip:

	def __init__(self, help, message):
		self.text = message

	def execute(self):
		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		ret = config.items('command-tip')

		return ret[random.randint(0,len(ret)-1)]