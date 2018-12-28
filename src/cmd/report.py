# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
from leadtime import Leadtime
from throughput import Throughput
from open import Open
from retro import Retro
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Report:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message
		self.average = None
		self.tags = None
		self.full = None
		self.from_date = None
		self.to_date = None

	def execute(self):
		barsize = 100
		title = ' *' + self.repo.ghrepo + '* '
		bar = (barsize - len(title)) / 2
		ret = '\n\n' + ('_' * bar) + title + ('_' * bar) + '\n'

		title = ' *Tempo de espera* '
		bar = (barsize - len(title)) / 2
		ret += '\n\n' + ('_' * bar) + title + ('_' * bar) + '\n'
		command = Leadtime(self.repo, self.text)
		setattr(command, 'average', self.average)
		setattr(command, 'tags', self.tags)
		setattr(command, 'full', self.full)
		setattr(command, 'from_date', self.from_date)
		setattr(command, 'to_date', self.to_date)
		ret += command.execute()

		title = ' *Vazão* '
		bar = (barsize - len(title)) / 2
		ret += '\n\n' + ('_' * bar) + title + ('_' * bar) + '\n'
		command = Throughput(self.repo, self.text)
		setattr(command, 'average', self.average)
		setattr(command, 'tags', self.tags)
		setattr(command, 'full', self.full)
		setattr(command, 'from_date', self.from_date)
		setattr(command, 'to_date', self.to_date)
		ret += command.execute()

		title = ' *Backlog atual* '
		bar = (barsize - len(title)) / 2
		ret += '\n\n' + ('_' * bar) + title + ('_' * bar) + '\n'
		command = Open(self.repo, self.text)
		setattr(command, 'tags', self.tags)
		ret += command.execute()		

		title = ' *Retrospectivas* '
		bar = (barsize - len(title)) / 2
		ret += '\n\n' + ('_' * bar) + title + ('_' * bar) + '\n'
		command = Retro(self.repo, self.text)
		ret += command.execute()		

		title = ' *FIM* '
		bar = (barsize - len(title)) / 2
		ret += '\n\n' + ('_' * bar) + title + ('_' * bar) + '\n'


		return ret
