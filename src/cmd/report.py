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

    def execute(self):
        ret = 'Report do time *' + self.repo.ghrepo.upper() + '*'

        ret += '\n\n--- *Tempo de espera* ----------------------------------\n'
        command = Leadtime(self.repo, self.text)
        setattr(command, 'average', self.average)
        setattr(command, 'tags', self.tags)
        setattr(command, 'full', self.full)
        ret += command.execute()

        ret += '\n\n--- *Vazão* ----------------------------------\n'
        command = Throughput(self.repo, self.text)
        setattr(command, 'average', self.average)
        setattr(command, 'tags', self.tags)
        setattr(command, 'full', self.full)
        ret += command.execute()

        ret += '\n\n--- *Backlog atual* ----------------------------------\n'
        command = Open(self.repo, self.text)
        setattr(command, 'tags', self.tags)
        ret += command.execute()        

        ret += '\n\n--- *Retrospectivas* ----------------------------------\n'
        command = Retro(self.repo, self.text)
        ret += command.execute()        

        return ret
