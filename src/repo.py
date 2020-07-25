# -*- coding: utf-8 -*-

import ConfigParser
import re
import os
import json
import requests
import re
from datetime import datetime, timedelta

class Repo:

	def __init__(self, ghrepo):
		self.ghrepo = ghrepo

		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		self.average = config.getint('github', 'average')
		self.retro_relative_urls = config.get('github', 'retro.relative.urls')