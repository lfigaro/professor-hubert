import os
import json
import requests
import re
import copy
import boto
import ssl

from boto.s3.key import Key
from datetime import datetime, timedelta

class Offline_metrics:

	def __init__(self, repo, event):
		self.event = event
		self.repo = repo

	def execute(self):
		event = self.event

		squadRepo = None
		if 'squadRepo' in event:
			squadRepo = event['squadRepo']
		else:
			oldExecutions = self.open_from_bucket('execution')

			url = 'https://api.github.com/search/repositories?per_page=500&q=org:' + os.environ['gh_organization'] + ' chapter OR squad in:name'
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
			data = response.json()
			for repo in data['items']:
				if (repo['name'] not in oldExecutions):
					squadRepo = repo['name'];
					break;
				else:
					if squadRepo is None or \
					   datetime.strptime(oldExecutions[repo['name']], '%Y-%m-%dT%H:%M:%SZ') < datetime.strptime(oldExecutions[squadRepo], '%Y-%m-%dT%H:%M:%SZ'):
					   squadRepo = repo['name']
		
		from_date = datetime.now().replace(hour=00, minute=00, second=00) - timedelta(days=90)
		to_date = datetime.now().replace(hour=23, minute=59, second=59)

		ret = {'fromDate': from_date.strftime('%Y-%m-%d'),
				 'toDate':   to_date.strftime('%Y-%m-%d')}
		tags = self.getLabels(squadRepo)
		ret['tags'] = tags
		ret['issues'] = self.getIssueEvents(squadRepo, from_date, to_date, tags)
		self.save_to_bucket(squadRepo, ret)

		oldExecutions[squadRepo] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
		self.save_to_bucket('execution', oldExecutions)

		return ret

	# Retorna as labels das issues do Repositorio selecionado
	def getLabels(self, squadRepo):
		ret = []
		
		url = 'https://api.github.com/repos/' + os.environ['gh_organization']  + '/' + squadRepo + '/labels'
		response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
		data = response.json()

		for label in data:
			ret.append(label['name'])

		return ret

	# Retorna dados das issues abertas
	def getIssueEvents(self, squadRepo, from_date, to_date, tags):
		issues = {}

		tagsArray = {'assigned': 0, 'unassigned': 0}
		tagsArrayTemp = {'assigned': [None, None]}
		for tag in tags:
			tagsArray[tag] = 0
			tagsArrayTemp[tag] = [None, None]

		url = 'https://api.github.com/repos/' + os.environ['gh_organization']  + '/' + squadRepo + '/issues?per_page=100&since=' + \
				from_date.strftime('%Y-%m-%dT%H:%M:%SZ') + '&state=closed&sort=created&direction=asc'

		while url is not None:
			response = requests.get(url, auth=(os.environ['user'], os.environ['pass']))
			data = response.json()

			link = response.headers.get('link', None)
			if link is not None:
				url = self.next_page(link)
			else:
				url = None

			for issue in data:
				issueTagsArray = copy.deepcopy(tagsArray)
				issueTagsArrayTemp = copy.deepcopy(tagsArrayTemp)

				issues[issue['number']] = {'closed_at': issue['closed_at'], 'tagsDistribution': issueTagsArray}

				url2 = 'https://api.github.com/repos/' + os.environ['gh_organization']  + '/' + squadRepo + '/issues/' + str(issue['number']) + '/events?per_page=500'

				while url2 is not None:
					response2 = requests.get(url2, auth=(os.environ['user'], os.environ['pass']))
					dataEvnt = response2.json()

					link2 = response2.headers.get('link', None)
					if link2 is not None:
						url2 = self.next_page(link2)
					else:
						url2 = None

					for event in dataEvnt:
						if event['event'] in ['labeled', 'unlabeled']\
							and 'label' in event and event['label']['name'] in tags:

							if event['event'] == 'labeled':
								issueTagsArrayTemp[event['label']['name']][0] = event['created_at']

							if event['event'] == 'unlabeled':
								if issueTagsArrayTemp[event['label']['name']][0] is not None:
									issueTagsArrayTemp[event['label']['name']][1] = event['created_at']
									dateA = datetime.strptime(issueTagsArrayTemp[event['label']['name']][0], '%Y-%m-%dT%H:%M:%SZ')
									dateB = datetime.strptime(issueTagsArrayTemp[event['label']['name']][1], '%Y-%m-%dT%H:%M:%SZ')
									delta = dateB - dateA

									issueTagsArray[event['label']['name']] += delta.seconds
									
									issueTagsArrayTemp[event['label']['name']] = [None, None]

						if event['event'] in ['assigned', 'unassigned']:

							if event['event'] == 'assigned':
								issueTagsArrayTemp['assigned'][0] = event['created_at']

							if event['event'] == 'unassigned':
								if issueTagsArrayTemp['assigned'][0] is not None:
									issueTagsArrayTemp['assigned'][1] = event['created_at']
									dateA = datetime.strptime(issueTagsArrayTemp['assigned'][0], '%Y-%m-%dT%H:%M:%SZ')
									dateB = datetime.strptime(issueTagsArrayTemp['assigned'][1], '%Y-%m-%dT%H:%M:%SZ')
									delta = dateB - dateA

									issueTagsArray['assigned'] += delta.seconds

									issueTagsArrayTemp['assigned'] = [None, None]

					for key in issueTagsArrayTemp:
						if issueTagsArrayTemp[key][0] is not None and issueTagsArrayTemp[key][1] is None:
							dateA = datetime.strptime(issueTagsArrayTemp[key][0], '%Y-%m-%dT%H:%M:%SZ')
							dateB = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
							delta = dateB - dateA

							issueTagsArray[key] += delta.seconds

					dateA = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
					dateB = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
					delta = dateB - dateA

					issueTagsArray['unassigned'] = (delta.seconds - issueTagsArray['assigned'])

		return issues

	def next_page(self, link):
		matchObj = re.search( r'\<[^<]*?\>; rel="next"', link , re.M|re.I )

		if matchObj:
			return matchObj.group().replace('<','').replace('>; rel="next"','')
		else:
			return None

	def save_to_bucket(self, file, data):
		bucketName = os.environ['bucket_name']
		keyId  = os.environ['aws_access_key_id']
		sKeyId = os.environ['aws_secret_access_key']
		fileName = 'data/' + file + ".json"

		conn = boto.s3.connect_to_region('us-east-1',
		   aws_access_key_id=keyId,
		   aws_secret_access_key=sKeyId,
		   is_secure=True,
		   calling_format = 'boto.s3.connection.OrdinaryCallingFormat'
		)

		bucket = conn.get_bucket(bucketName)

		#Get the Key object of the bucket
		k = Key(bucket)
		#Crete a new key with id as the name of the file
		k.key = fileName
		#Upload the file
		result = k.set_contents_from_string(json.dumps(data))
		#result contains the size of the file uploaded

	def open_from_bucket(self, file):
		bucketName = os.environ['bucket_name']
		keyId  = os.environ['aws_access_key_id']
		sKeyId = os.environ['aws_secret_access_key']
		fileName = 'data/' + file + ".json"

		
		conn = boto.s3.connect_to_region('us-east-1',
		   aws_access_key_id=keyId,
		   aws_secret_access_key=sKeyId,
		   is_secure=True,
		   calling_format = 'boto.s3.connection.OrdinaryCallingFormat'
		)

		bucket = conn.get_bucket(bucketName)
		#Get the Key object of the given key, in the bucket
		k = Key(bucket,fileName)
		#Get the contents of the key into a file 
		return json.loads(k.get_contents_as_string())
