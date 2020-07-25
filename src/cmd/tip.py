# -*- coding: utf-8 -*-

import ConfigParser
import random
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')

class Tip:

	def __init__(self, help, message):
		self.text = message
		self.subject = None

	def execute(self):
		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		tips = config.items('command-tips')

		if self.subject is not None:
			ret = []
			for key, value in tips:
				matchObj = re.search( key, self.subject , re.M|re.I )
				
				if matchObj:
					ret.append( value )
		else:
			ret = tips

		return ret[random.randint(0,len(ret)-1)]