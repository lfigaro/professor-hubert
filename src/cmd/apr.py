# -*- coding: utf-8 -*-

import json
import os
import requests
from datetime import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Apr:

    def __init__(self, repo, message):
        self.repo = repo
        self.text = message

    def execute(self):
        ret = self.repo.get_apr()

        if ret is not None:
            response = requests.get(ret['download_url'], auth=(os.environ['user'], os.environ['pass']))
            ret = 'Link do documento: ' + ret['html_url'] + '\n\n'
            ret += response.text
        else:
            ret = 'O time ' + squadRepo + ' não tem um APR :-('

        return ret