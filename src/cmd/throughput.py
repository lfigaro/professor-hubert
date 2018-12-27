# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sys
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')

class Throughput:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message
		self.average = None
		self.tags = None
		self.full = None

	def execute(self):
		try:
			if self.average is None:
				self.average = self.repo.average

			data = self.repo.closed_issues(average=self.average, tags=self.tags)

			if 'message' in data and data['message'] == 'Not Found':
				return 'Não existe nenhum time *' + self.repo.ghrepo + '* no GitHub. Se deseja a vazão de outro time, ' + \
					   'é só perguntar "qual a vazão do time xxxxxx ?"'		

			else:
				if self.full is not None:
					return self.get_full(data)
				else:
					return self.get_simple(data)

		except:
			e = sys.exc_info()
			traceback.print_exc()
			return 'Houve algum erro ao retornar a vazão do time ' + self.repo.ghrepo + ': ' + u"{}".format(e)


	def get_simple(self, data):
		if 'throughput' in data:

			thr = data['throughput']
			keys = thr.keys()
			keys.sort()
			
			first = thr[keys[0]][0][0]
			last = thr[keys[len(keys)-1]][0][0]

			ret = 'Análise de entrega de itens de valor do time *{}*\n'.format(self.repo.ghrepo)
			
			if first < 1:
				ret += 'Ha {} dias, o time entregava *1 item a cada {:.1f} dias* \n'.format(self.average, 1/first)
			else:
				ret += 'Ha {} dias, o time entregava *{:.1f} itens por dia* \n'.format(self.average, first)

			if last < 1:
				ret += 'Hoje o time entrega *1 item a cada {:.1f} dias* \n'.format(1/last)
			else:
				ret += 'Hoje o time entrega *{:.1f} itens por dia* \n'.format(last)

			if (first/last) < 0.9:
				ret += 'O time está entregando *mais* valor para seu "cliente". _HOORRAAYYY!_ :partyparrot:'
			elif (first/last) > 1.1:
				ret += 'O time está entregando *menos* valor para seu "cliente". _saaaaad..._ :sad-denis:'
			else:
				ret += 'O time está entregando valor *de forma consistente*. _HOORRAAYYY!_ :partyparrot:'


		return ret


	def get_full(self, data):
		if 'throughput' in data:
			ret1 = 'Análise da *vazão* dos ultimos *' + str(self.average) + ' dias* para o time *' + self.repo.ghrepo + '*'
			if self.tags is not None:
				ret1 += ' filtrando pelas tags *' + self.tags + '*'
			ret1 += ': \n'
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
					ret3 += 'O time está entregando *' + str(int(end)) + '% menos itens* do que nos ' + str(self.average) + ' dias anteriores :disappointed:\n'
				elif end > 0:
					ret3 += 'O time está entregando *' + str(int(end)) + '% mais itens* do que nos ' + str(self.average) + ' dias anteriores :smiley:\n'

		ret = ret1 + '\n' + ret3 + '\n' + ret2 + ret4

		return ret

