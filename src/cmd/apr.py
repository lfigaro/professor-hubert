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
        url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.repo.ghrepo + '/contents/agl/apr'
        response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
        data = response.json()

        ret = None
        if 'message' in data and 'Not Found' == data['message']:            
            ret = 'Não foi encontrado um time ' + self.repo.ghrepo + ' ou ele não tem um APR :-('

        else:
            prvWhen = None
            for apr in data:
                url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.repo.ghrepo + '/commits?path=' + apr['path']
                response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
                commits = response.json()

                when = datetime.strptime(commits[0]['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
                if prvWhen is None or prvWhen < when:
                    prvWhen = when
                    ret = apr

            if ret is not None:
                response = requests.get(ret['download_url'], auth=(os.environ['user'], os.environ['pass']))
                ret = 'Link do documento: ' + ret['html_url'] + '\n\n'
                ret += response.text
            else:
                ret = 'O time ' + squadRepo + ' não tem um APR :-('

        return ret