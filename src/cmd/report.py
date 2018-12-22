# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
from leadtime import Leadtime
from throughput import Throughput
from open import Open
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Report:

    def __init__(self, repo, message):
        self.repo = repo
        self.text = message

    def execute(self):
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
