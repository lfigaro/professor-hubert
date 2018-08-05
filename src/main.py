import ConfigParser
import re
import sys
import importlib
import repo

def handler(event, context):
    command = findCommand(event)
    print command.execute()


# Identify if the message contains the command
def findCommand(message):
    config = ConfigParser.RawConfigParser()
    config.read('command.cfg')
    commands = config.items('commands')

    command = None
    for key, value in commands:
        ret = re.search(key, message)
        
        if (ret is not None):
            class_ = getattr(importlib.import_module("cmd." + value), value.capitalize())
            command = class_(repo.Repo(message), message)

    return command

if __name__ == "__main__":
    args = ''
    for index in range(len(sys.argv)):
        if index > 0:
            args += sys.argv[index] + ' '

    handler(args, None)