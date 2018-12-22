# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import logging
import json
from leadtime import Leadtime
from throughput import Throughput
from open import Open


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Report:

    def __init__(self, repo, message):
        self.repo = repo
        self.text = message

    def execute(self):
        repo = self.repo.ghrepo
        msg = self.text

        data = self.repo.closed_issues(fromDateObj=None, toDateObj=None, tags=[], average=None)

        ret = '\n--- *Leadtime* ----------------------------------\n'
        
        command = Leadtime(self.repo, self.text)
        ret += command.execute()

        ret += '\n--- *Throughput* ----------------------------------\n'
        command = Throughput(self.repo, self.text)
        ret += command.execute()

        ret += '\n--- *Open Issues* ----------------------------------\n'
        command = Open(self.repo, self.text)
        ret += command.execute()        
        
        return ret
