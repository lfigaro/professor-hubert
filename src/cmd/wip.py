# -*- coding: utf-8 -*-

import json
import os
import re
import requests
from datetime import datetime
import sys
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')

class Wip:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message
		self.list = None

	def execute(self):
		try:
			issues = self.repo.open_issues()

			wip = 0
			wipList = {}
			for issue in issues['openIssues']:
				if issue['assignee'] is not None:
					if list is None:
						wip += 1

					else:
						if issue['assignee'] in wipList:
							wipList[issue['assignee']] += 1
						else:
							wipList[issue['assignee']] = 1

			ret = None
			if self.list is None:
				ret = 'O time tem ' + str(wip) + ' items em progresso.\n'
			else:
				ret = 'Items atribuidos:\n'
				for key, value in wipList.items():
					ret += key + ' - ' + str(value) + ' items.\n' 

			return ret

		except:
			e = sys.exc_info()
			traceback.print_exc()
			return 'Houve algum erro ao retornar o WIP do time ' + self.repo.ghrepo + ': ' + u"{}".format(e)