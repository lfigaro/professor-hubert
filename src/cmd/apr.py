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

class Apr:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message
		self.list = None

	def execute(self):
		try:
			docs = self.repo.get_apr()
			docs = docs['aprs']

			if docs is not None:
				if self.list is not None:
					ret = self.list_retro(docs)
				else:
					ret = self.get_retro(docs)

			else:
				ret = 'O time ' + self.repo.ghrepo + ' não tem um APR :-('

			return ret

		except:
			e = sys.exc_info()
			traceback.print_exc()
			return 'Houve algum erro ao retornar os APRs do time ' + self.repo.ghrepo + ': ' + u"{}".format(e)


	def list_retro(self, docs):
		keys = docs.keys()
		keys.sort()

		ret = 'Lista de APRs do time *{}*\n\n'.format(self.repo.ghrepo)
		for key in keys:
			doc = docs[key]
			ret += '*' + key + '* - ' + doc['html_url'] + '\n'
		return ret


	def get_retro(self, docs):
		keys = docs.keys()
		keys.sort()
		d = keys[len(keys)-1]
		doc = docs[d]

		response = requests.get(doc['download_url'], auth=(os.environ['user'], os.environ['pass']))
		ret = 'Data do ultimo APR: *' + d + '*  \n'
		ret += 'Link do documento: ' + doc['html_url'] + '\n\n'

		if response.text is not None:
			doc = response.text
			matchObjLst = re.findall( r'\- \[ \] .+', doc , re.M|re.I )
			if matchObjLst:
				ret += '*Plano de ações:*\n\n'
			for matchObj in matchObjLst:
				ret += matchObj + '\n'

		return ret