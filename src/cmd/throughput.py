# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

class Throughput:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message

	def execute(self):
		data = self.repo.closed_issues(fromDateObj=None, toDateObj=None, tags=[], average=None)

		if 'message' in data and data['message'] == 'Not Found':
			return 'Não existe nenhum time *' + self.repo.ghrepo + '* no GitHub. Se deseja a vazão de outro time, ' + \
				   'é só perguntar "qual a vazão do time xxxxxx ?"'		

		else:
			if 'throughput' in data:
				ret1 = 'Análise da *vazão* dos ultimos *7 dias* para o time *' + self.repo.ghrepo + '*: \n'
				ret2 = 'Histórias entregues por dia: '
				ret4 = ':thumbsup: indica vazão *acima* da média, :thumbsdown: indica vazão *abaixo* da média \n'
				thr = data['throughput']
				keys = thr.keys()
				keys.sort()
				
				first = None
				last = None
				previous = 0
				for key in keys:
					d = thr[key][1]
					last = thr[key][0][0]
					if first == None:
						first = thr[key][0][0]

					trend = ''
					if first is None:
						trend = ''
					elif first == d:
						trend = ''
					elif first < d :
						trend = ':thumbsup:'
					elif first > d:
						trend = ':thumbsdown:'

					ret2 += '*' + str(int(d)) + '* ' + trend +', '

				ret2 = ret2[:-2] + '\n'

				ret3 = 'Média no início do período: *' + "{0:.2f}".format(first) + ' itens*. Média no fim do período: *' + "{0:.2f}".format(last) + ' itens* \n'

				if last != 0 and first == 0:
					ret3 += 'O time voltou à ativa depois de um tempo sem entregas :the_horns:\n'
				elif last == 0 or first == 0:
					ret3 += 'O time não entrega nada faz um tempo. QUEQUITACONTECENO?!? :scream:\n'
				else:
					end = (((last / first) -1) * 100)
					if end == 0:
						ret3 += 'O time está com sua *vazão estável* :punch:\n'
					elif end < 0:
						end = end * -1
						ret3 += 'O time está entregando *' + str(int(end)) + '% menos itens* do que nos 7 dias anteriores :disappointed:\n'
					elif end > 0:
						ret3 += 'O time está entregando *' + str(int(end)) + '% mais itens* do que nos 7 dias anteriores :smiley:\n'
			
			ret = ret1 + '\n' + ret3 + '\n' + ret2 + ret4
			
			return ret
