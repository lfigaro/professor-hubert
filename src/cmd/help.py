import ConfigParser

class Help:

	def __init__(self, help, message):
		self.text = message

	def execute(self):
		config = ConfigParser.RawConfigParser()
		config.read('command.cfg')
		ret = config.get('command-help', 'help-text')

		return ret