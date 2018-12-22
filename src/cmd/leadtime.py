# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

class Leadtime:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message

	def execute(self):
		repo = self.repo.ghrepo
		msg = self.text

		data = self.repo.closed_issues(fromDateObj=None, toDateObj=None, tags=[], average=None)

		if 'message' in data and data['message'] == 'Not Found':
			return 'Não existe nenhum time *' + self.repo.ghrepo + '* no GitHub. Se deseja o leadtime de outro time, ' + \
				   'é só perguntar "qual o leadtime do time xxxxxx?"'
			
		else:
			if 'leadtime' in data:

				ret1 = 'Análise do *leadtime* dos ultimos *7 dias* para o time *' + self.repo.ghrepo + '*: \n'
				ret2 = 'Leadtime de histórias entregues: '
				ret4 = ':thumbsup: indica leadtime *abaixo* da média, :thumbsdown: indica leadtime *acima* da média.\n'

				thr = data['leadtime']
				keys = thr.keys()
				keys.sort()
				
				first = None
				last = None
				previous = 0

				for key in keys:
					last = thr[key][0][0]
					if first == None:
						first = thr[key][0][0]

					for idx, val in enumerate(thr[key]):
						if idx > 0:
							d = thr[key][idx][1]

							trend = ''
							if first is None:
								trend = ''
							elif first == d:
								trend = ''
							elif first > d :
								trend = ':thumbsup:'
							elif first < d:
								trend = ':thumbsdown:'

							ret2 += '*' + str(int(d)) + '* ' + trend +', '
							
				ret2 = ret2[:-2] + '\n'

				ret3 = 'Média no início do período: *' + "{0:.2f}".format(first) + ' dias*. Média no fim do período: *' + "{0:.2f}".format(last) + ' dias* \n'

				if last is None:
					ret3 += 'O time não entrega nada faz um tempo. QUEQUITACONTECENO?!? :scream:\n'
				elif last is not None and first is None:
					ret3 += 'O time voltou à ativa depois de um tempo sem entregas :the_horns:\n'
				else:
					end = (((float(last) / float(first)) -1) * 100)
					if end == 0:
						ret3 += 'O time está com seu *leadtime estável* :punch:\n'
					elif end > 0:
						ret3 += 'O time está entregando *' + "{0:.2f}".format(float(end)) + '% mais devagar* do que a 7 dias atrás :disappointed:\n'
					elif end < 0:
						end = end * -1
						ret3 += 'O time está entregando em média *' + "{0:.2f}".format(float(end)) + '% mais rápido* do que a 7 dias atrás :smiley:\n'

				ret3 += '_Lembrando que no caso de leadtime, quanto menor o número mais rápido_ \n'

			ret = ret1 + '\n' + ret3 + '\n' + ret2 + ret4
			
			return ret
