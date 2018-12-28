# -*- coding: utf-8 -*-

import ConfigParser
import re
import os
import json
import requests
import re
from datetime import datetime, timedelta

class Repo:

	def __init__(self, ghrepo):
		self.ghrepo = ghrepo

		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		average = config.getint('github', 'average')
		self.average = average

	def get_apr(self):
		url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/contents/agl/apr'
		response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
		data = response.json()

		ret = None
		if not('message' in data and 'Not Found' == data['message']):
			ret={}
			prvWhen = None
			for apr in data:
				url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/commits?path=' + apr['path']
				response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
				commits = response.json()

				when = datetime.strptime(commits[0]['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
				if prvWhen is None or prvWhen < when:
					prvWhen = when
					ret[prvWhen.strftime("%Y-%m-%d")] = apr
		
		return ret

	def get_retro(self, from_date=None, to_date=None):
		if to_date is None:
			to_date = datetime.now().replace(hour=23, minute=59, second=59)
		else:
			to_date = datetime.strptime(to_date, "%Y-%m-%d")
		
		if from_date is None:
			from_date = datetime.now().replace(hour=00, minute=00, second=00) - timedelta(days=180)
		else:
			from_date = datetime.strptime(from_date, "%Y-%m-%d")


		url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/contents/agl/retro'
		response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
		data = response.json()

		ret = None
		if not('message' in data and 'Not Found' == data['message']):
			ret={}
			prvWhen = None
			for retro in data:
				url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/commits?path=' + retro['path']
				response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
				commits = response.json()

				when = datetime.strptime(commits[0]['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
				if (prvWhen is None or prvWhen < when) and when > from_date and when < to_date:
					prvWhen = when
					ret[prvWhen.strftime("%Y-%m-%d")] = retro
		
		return ret

	def get_repos(self):
		ret = []

		url = 'https://api.github.com/search/repositories?per_page=500&q=org:' + os.environ['gh_organization'] + \
			  ' chapt OR squad in:name'

		while url is not None:
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
			data = response.json()

			for repo in data['items']:
				ret.append(repo['name'])

			link = response.headers.get('link', None)
			if link is not None:
				url = next_page(link)
			else:
				url = None

		return {'repos': ret}

	# Retorna as labels das issues do Repositorio selecionado
	def get_labels(self):
		ret = []
		
		url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/labels'

		while url is not None:
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))  
			data = response.json()  
			link = response.headers.get('link', None)
			if link is not None:
				url = next_page(link)
			else:
				url = None

			for label in data:
				ret.append(label['name'])

		return ret

	# Retorna dados das issues abertas
	def open_issues(self, tags=None):
		if tags is not None:
			tags = tags.split(',')
		else:
			tags = []
		
		issues = []
		leadtime = []

		url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/issues?per_page=100' + \
				'&state=open&sort=created&direction=asc'

		while url is not None:
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
			data = response.json()

			link = response.headers.get('link', None)
			if link is not None:
				url = next_page(link)
			else:
				url = None

			prog = tag_regex(tags)
			for issue in data:			
				if prog.search(str(issue['labels']).replace('u\'','\'')) is not None and 'pull_request' not in issue:
					dateCreated = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
					dateCurrent = datetime.now()
					delta = dateCurrent - dateCreated

					issues.append({'issue': issue['number'], 
									'created_at': issue['created_at'],
									'leadtime': delta.days})

					leadtime.append(delta.days)

		return {'leadtime': [mean(leadtime), stddev(leadtime)], 'openIssues': issues}

	# Retorna dados das issues abertas
	def get_cfd(self, from_date=None, to_date=None, tags=None, average=None):
		if average is None:
			average = self.average
		else:
			average=int(average)

		if to_date is None:
			to_date = datetime.now().replace(hour=23, minute=59, second=59)
		else:
			to_date = datetime.strptime(to_date, "%Y-%m-%d")
		
		if from_date is None:
			from_date = datetime.now().replace(hour=00, minute=00, second=00) - timedelta(days=average)
		else:
			from_date = datetime.strptime(from_date, "%Y-%m-%d")

		if tags is not None:
			tags = tags.split(',')
		else:
			tags = []

		issues = []

		url = 'https://api.github.com/repos/'+ os.environ['gh_organization'] + '/' + self.ghrepo + '/issues?per_page=100&since=' + \
				from_date.strftime('%Y-%m-%dT%H:%M:%SZ') + '&state=closed&sort=created&direction=asc'

		self.run_cfd(url, tags, issues)

		url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/issues?per_page=100' + \
				'&state=open&sort=created&direction=asc'

		self.run_cfd(url, tags, issues)

		return {'dateFrom': from_date.strftime('%Y-%m-%d'), \
		  'dateTo': to_date.strftime('%Y-%m-%d'), \
		  'cfd': issues}

	def run_cfd(self, url, tags, issues):
		while url is not None:
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
			data = response.json()

			link = response.headers.get('link', None)
			if link is not None:
				url = next_page(link)
			else:
				url = None

			prog = tag_regex(tags)
			for issue in data:			
				if prog.search(str(issue['labels']).replace('u\'','\'')) is not None and 'pull_request' not in issue:

				#if prog.search(str(issue['labels'])) is not None and 'pull_request' not in issue:
					issueArr = {'issue': issue['number'], \
								'created_at': issue['created_at'].split('T')[0]}

					if issue['closed_at'] is not None:
						issueArr['closed_at']=(issue['closed_at'].split('T')[0])

					if ('assignee' in issue and issue['assignee'] is not None):
						url2 = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/issues/' + str(issue['number']) + '/events?per_page=500'
						response2 = requests.get(url2, auth=(os.environ['user'], os.environ['pass']))
						dataEvnt = response2.json()

						dateAssigned = None

						for event in dataEvnt:
							if event['event'] == 'assigned':
								issueArr['assigned_at'] = event['created_at'].split('T')[0]
								break

					issues.append(issueArr)

	# Retorna dados das issues fechadas
	def closed_issues(self, from_date=None, to_date=None, tags=None, average=None):
		if average is None:
			average = self.average
		else:
			average=int(average)

		if to_date is None:
			to_date = datetime.now().replace(hour=23, minute=59, second=59)
		else:
			to_date = datetime.strptime(to_date, "%Y-%m-%d")
		
		if from_date is None:
			from_date = datetime.now().replace(hour=00, minute=00, second=00) - timedelta(days=average)
		else:
			from_date = datetime.strptime(from_date, "%Y-%m-%d")

		if tags is not None:
			tags = tags.split(',')
		else:
			tags = []

		# Cria objetos que vão ser retornados
		throughput = {}
		thrAvgHelper = {}
		ltAvgHelper = {}
		leadtime = {}
		ret = {'self.repo.ghrepo': self.ghrepo ,'tagsTitles': tags, 'throughput' : throughput, 'leadtime': leadtime}
		from_dateAvg = from_date - timedelta(days=(average-1))

		# Preenche com as chaves iniciais
		d = from_dateAvg
		while d <= to_date:
			tagsRet = [0] * len(tags)
			thrAvgHelper[d.strftime("%Y-%m-%d")] = [0, tagsRet]
			ltAvgHelper[d.strftime("%Y-%m-%d")] = []
			if d >= from_date:
				tagsRet = [0] * len(tags)
				throughput[d.strftime("%Y-%m-%d")] = [None,0,tagsRet]
				leadtime[d.strftime("%Y-%m-%d")] = [None]
			d += timedelta(days=1)

		# Busca os dados no GitHub
		url = 'https://api.github.com/repos/' + os.environ['gh_organization'] + '/' + self.ghrepo + '/issues?per_page=500&state=closed&since=' + from_dateAvg.strftime('%Y-%m-%dT%H:%M:%SZ')
		
		while url is not None:
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
			data = response.json()

			link = response.headers.get('link', None)
			if link is not None:
				url = next_page(link)
			else:
				url = None

			# No caso de erros
			if 'message' in data and 'Not Found' == data['message']:			
				return data

			prog = tag_regex(tags)

			# Trabalha no retorno da busca do GH
			for issue in data:
				if (prog.search(str(issue['labels']).replace('u\'','\'')) is not None and 'pull_request' not in issue) :

					created_at = issue['created_at']
					closed_at = issue['closed_at']

					dateCreated = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
					dateClosed = datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ')
					dateClosedFormated = dateClosed.strftime("%Y-%m-%d")

					delta = dateClosed - dateCreated
					if dateClosed <= to_date and dateClosed >= from_dateAvg:
						#LEADTIME-AVG
						ltAvgHelper[dateClosedFormated].append(delta.days)

						#THROUGHPUT-AVG
						days = thrAvgHelper[dateClosedFormated][0]
						days = days + 1
						thrAvgHelper[dateClosedFormated][0] = days
						for idTag, tag in enumerate(tags):
							for label in issue['labels']:
								if (label['name']==tag):
									days = thrAvgHelper[dateClosedFormated][1][idTag]
									days = days + 1
									thrAvgHelper[dateClosedFormated][1][idTag] = days

					if dateClosed <= to_date and dateClosed >= from_date:
						#LEADTIME
						leadtime[dateClosedFormated].append([issue['number'], delta.days])

						#THROUGHPUT
						days = throughput[dateClosedFormated][1]
						days = days + 1
						throughput[dateClosedFormated][1] = days

		# Calcula as médias
		keysSorted = thrAvgHelper.keys()
		keysSorted.sort()

		# Média de throughput
		avg = []
		for x in range(0, len(keysSorted)):
			avg.append(thrAvgHelper[keysSorted[x]][0])
			if x >= (average-1):
				throughput[keysSorted[x]][0] = [mean(avg), stddev(avg)]
				del avg[0]

		for z in range(0, len(tags)):
			avg = []
			for x in range(0, len(keysSorted)):
				avg.append(thrAvgHelper[keysSorted[x]][1][z])
				if x >= (average-1):
					throughput[keysSorted[x]][2][z] = mean(avg)
					del avg[0]

		keysSorted = ltAvgHelper.keys()
		keysSorted.sort()

		# Media de Leadtime
		avg = []
		for x in range(0, len(keysSorted)):
			avg.append(ltAvgHelper[keysSorted[x]])
			if x >= (average - 1):
				avgHlp = []
				for y in range(0, average):
					avgHlp += avg[y]
				
				leadtime[keysSorted[x]][0] = [mean(avgHlp), stddev(avgHlp)]
				del avg[0]

		return ret

def tag_regex(tags):
	# Cria REGEX para busca das TAGS
	reg = ''
	for tag in tags:
		reg += '["|\']name["|\']: ["|\']' + tag + '["|\']|'
	prog = re.compile(reg[:-1])
	
	return prog

def next_page(link):
	matchObj = re.search( r'\<[^<]*?\>; rel="next"', link , re.M|re.I )
	
	if matchObj:
		return matchObj.group().replace('<','').replace('>; rel="next"','')
	else:
		return None

def mean(data):
	"""Return the sample arithmetic mean of data."""
	n = len(data)
	if n < 1:
		return None
	return sum(data)/float(n)

def _ss(data):
	"""Return sum of square deviations of sequence data."""
	c = mean(data)
	ss = sum((x-c)**2 for x in data)
	return ss

def stddev(data, ddof=0):
	"""Calculates the population standard deviation
	by default; specify ddof=1 to compute the sample
	standard deviation."""
	n = len(data)
	if n < 2:
		return None
	ss = _ss(data)
	pvar = ss/(n-ddof)
	return pvar**0.5