# Romário BOT

## O que é o Romário?

É um bot que pretende integrar o Google Analytics ao nosso slack para trazer, de forma fácil, informações de negócio :-)

<p align="center">
<img align="center" src="./html/img/romario.png" alt="É isso ai, peixe!">
</p>

## No seriously, what is Professor Hubert?

We wrote the first version of Professor to automate our company agile metrics based on GitHub flow control. Professor Hubert knew important team information such as leadtime, throughput, prediction on the current backlog based on current leadtime, last (actually all) retrospectives team made...OAh, and he gives you important tips about agile in general :-)

Today's version of Professor Hubert is open source, written in Python, and easily deployed on platforms like AWS lambda. More importantly, Professor Hubert is a very simple application for you to create your own commands.

## What can Professor Hubert do?

The possibilities are endless...well, maybe not that much, but they are pretty high!

Today all the commands are about consume GitHub API, do some math, format a little bit and that's it. But that's pretty cool, to be honest. Once we decided to use GitHub to even control our teams flow, Professor Hubert was a logical output since we didn't find any tools to help us measure ourselves.

## How do I write my own Professor Hubert commands?

Easy-peasy.

Include your command at src/command.cfg file. Make sure to write a cool regex in order to your command sound like a small talk (how cool is to ask "Professor, make damn sure to check my current open issues are below average leadtime, or I'll kill ya").

Once your command is setup, create a command file under src/cmd/ directory (Make sure your command have the same file and class name as the one you setup) and start code :-)

## But how it works?

This is how the components interacts one each other.

<p align="center">
<img align="center" src="./html/img/professor-hubert.png">
</p>

## And if I want to host the application myself :thinking-face: 

Oh, I see...you don't...like...us :-(

Oh well, don't worry, this is simple too. Follow the installation steps:

- Create a lambda function
	- Change 'Handler' to 'main.handler'
	- On 'Environment variables', create the following ones:
		- *user*: username of a GitHub integration user that will close the issue.
		- *pass*: password of this user.
		- *gh_organization*: The name of you GitHub organization.
		- *sl_token*: Slack app token.
		- *sl_token_src*: Slack verification token.
- Give repositories view permisson to the user setup above.
- Create a AWS API Gateway function.
- Create a Slack App integrations.
	- Here is where you get slack app and verification tokens.
- On Slack App 'Event Subscriptions'
	- Setup the API Gateway URL at you slack Request URL
	- Add the events 'app.mention' and 'message.im'

## Credits

I created this when working on Grupo ZAP (<https://github.com/grupozap>).

Contributors:

- Grupo ZAP Agile SuperHero Team.
- Lots more, run `git shortlog -s` for a list!

## License

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation.
