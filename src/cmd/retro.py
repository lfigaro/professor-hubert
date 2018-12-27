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

class Retro:

    def __init__(self, repo, message):
        self.repo = repo
        self.text = message
        self.list = None

    def execute(self):
        try:
            docs = self.repo.get_retro()

            if docs is not None:
                if self.list is not None:
                    ret = self.list_retro(docs)
                else:
                    ret = self.get_retro(docs)

            else:
                ret = 'O time *' + self.repo.ghrepo + '* não tem retrospectivas\n'
                ret += '(Ou não as coloca no GitHub) :disappointed:'

            return ret

        except:
            e = sys.exc_info()
            traceback.print_exc()
            return 'Houve algum erro ao retornar as retrospectivas do time ' + self.repo.ghrepo + ': ' + u"{}".format(e)


    def list_retro(self, docs):
        keys = docs.keys()
        keys.sort()

        ret = 'Lista de retrospectivas do time *{}*\n\n'.format(self.repo.ghrepo)
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
        ret = 'Data da ultima retro: *' + d + '*  '

        dObj = datetime.strptime(d, '%Y-%m-%d')
        dateCurrent = datetime.now()
        delta = dateCurrent - dObj

        if delta.days<15:
            ret += '_Great Job_ :cool_jesus: \n'
        elif delta.days<30:
            ret += '_Could be better..._ :thinking_face: \n'
        elif delta.days>30:
            ret += '_Far, faaar away..._ :scream: \n'

        ret += 'Link do documento: ' + doc['html_url'] + '\n\n'

        if response.text is not None:
            doc = response.text
            matchObjLst = re.findall( r'\- \[ \] .+', doc , re.M|re.I )
            if matchObjLst:
                ret += '*Plano de ações da retro:*\n\n'
            for matchObj in matchObjLst:
                ret += matchObj + '\n'

        return ret
