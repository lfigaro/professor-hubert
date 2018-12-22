# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Open:

    def __init__(self, repo, message):
        self.repo = repo
        self.text = message

    def execute(self):
        repo = self.repo.ghrepo
        msg = self.text

        data = self.repo.closed_issues()

        ltAvg=0
        thAvg=0
        if 'message' in data and data['message'] == 'Not Found':
            return 'Não existe nenhum time *' + self.repo.ghrepo + '* no GitHub. Se deseja o leadtime de outro time, ' + \
                   'é só perguntar "qual o leadtime do time xxxxxx?"'

        else:
            if 'leadtime' in data:
                thr = data['leadtime']
                keys = list(thr)
                lastKey = len(keys) - 1
                keys.sort()
                ltAvg = thr[keys[lastKey]][0][0]

            if 'throughput' in data:
                thr = data['throughput']
                keys = list(thr)
                lastKey = len(keys) - 1
                keys.sort()
                thAvg = thr[keys[lastKey]][0][0]

        data = self.repo.open_issues(tags=[])

        if 'message' in data and data['message'] == 'Not Found':
            return 'Não existe nenhum time *' + self.repo.ghrepo + '* no GitHub. Se deseja o leadtime de outro time, ' + \
                   'é só perguntar "qual o leadtime do time xxxxxx?"'

        else:
            OIqty = 0
            OIHigherLeadtime = 0

            if 'leadtime' in data:
                ltOIAvg = data['leadtime'][0]

            if 'openIssues' in data:
                for issue in data['openIssues']:
                    OIqty += 1

                    if issue['leadtime'] > ltAvg:
                        OIHigherLeadtime += 1

        perc = (OIHigherLeadtime / OIqty) * 100

        if thAvg > 0:
            vaz = 'em *' +str(int(OIqty / thAvg) + 1) + ' dias*'
        else:
            vaz = '*NUNCA <o>*'

        ret1 = 'O time tem *' + str(int(OIqty)) + ' itens abertos* atualmente'
        ret2 = '*' + "{0:.2f}".format(perc) + '%* (*' + str(int(OIHigherLeadtime)) + ' itens*) dos itens abertos estão acima do leadtime médio de *' + "{0:.2f}".format(ltAvg) + ' dias*.'
        ret3 = 'Na vazão atual do time, os itens serão entregues ' + vaz
        
        return ret1 + '\n' + ret2 + '\n' + ret3
