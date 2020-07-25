# -*- coding: utf-8 -*-

import sys
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')

class Leadtime:

	def __init__(self, repo, message):
		self.repo = repo
		self.text = message
		self.average = None
		self.tags = None
		self.full = None
		self.from_date = None
		self.to_date = None

	def execute(self):
		try:
			if self.average is None:
				self.average = self.repo.average

			data = self.repo.closed_issues(average=self.average, tags=self.tags, from_date=self.from_date, to_date=self.to_date)

			if 'message' in data and data['message'] == 'Not Found':
				return 'Não existe nenhum time *' + self.repo.ghrepo + '* no GitHub. Se deseja o leadtime de outro time, ' + \
					   'é só perguntar "qual o leadtime do time xxxxxx?"'
				
			else:
				if self.full is not None:
					return self.get_full(data)
				else:
					return self.get_simple(data)

		except:
			e = sys.exc_info()
			traceback.print_exc()
			return 'Houve algum erro ao retornar o leadtime do time ' + self.repo.ghrepo + ': ' + u"{}".format(e)

	def get_simple(self, data):
		if 'leadtime' in data:

			thr = data['leadtime']
			keys = thr.keys()
			keys.sort()
			
			first = thr[keys[0]][0][0]
			last = thr[keys[len(keys)-1]][0][0]

			ret = 'Percepção do tempo para entrega valor do time *{}*\n'.format(self.repo.ghrepo)
			
			if first < 1:
				ret += 'Ha {} dias, a percepção era de que o time entregava o que se comprometia em menos de um dia.'.format(self.average)
			else:
				ret += 'Ha {} dias, a percepção era de que o time entregava o que se comprometia em *{:.1f} dias* \n'.format(self.average, first)

			if last < 1:
				ret += 'Hoje a percepção é que o time entrega o que se compromete em menos de um dia.'
			else:
				ret += 'Hoje a percepção é que o time entrega o que se compromete em *{:.1f} dias* \n'.format(last)

			if (first/last) < 0.9:
				ret += 'A percepção é de que o time está levando *mais tempo* para entregar um item de valor. _#OhNooo!_ :ataque:'
			elif (first/last) > 1.1:
				ret += 'A percepção é de que o time está levando *menos tempo* para entregar um item de valor. _#LikeABoss!_ :like_a_boss:'
			else:
				ret += 'A percepção é de que o time está entregando valor *de forma consistente*. _#LikeABoss!_ :like_a_boss:'

		return ret

	def get_full(self, data):
		if 'leadtime' in data:

			ret1 = 'Análise do *leadtime* dos ultimos *' + str(self.average) + ' dias* para o time *' + self.repo.ghrepo + '*'
			if self.tags is not None:
				ret1 += ' filtrando pelas tags *' + self.tags + '*'
			ret1 += ': \n'
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

			if first is None and last is None:
				ret = 'O time não teve entregas nos ultimos ' + str(self.average) + ' dias :-('
			else:
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
						ret3 += 'O time está entregando *' + "{0:.2f}".format(float(end)) + '% mais devagar* do que a ' + str(self.average) + '  dias atrás :disappointed:\n'
					elif end < 0:
						end = end * -1
						ret3 += 'O time está entregando em média *' + "{0:.2f}".format(float(end)) + '% mais rápido* do que a ' + str(self.average) + ' dias atrás :smiley:\n'

				ret3 += '_Lembrando que no caso de leadtime, quanto menor o número mais rápido_ \n'

				ret = ret1 + '\n' + ret3 + '\n' + ret2 + ret4
		
		return ret

