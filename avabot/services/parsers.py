# -*- coding: utf-8 -*-
import shlex
import docopt

from avabot import __author__, __author_email__
from avabot import __version__
from avabot.exceptions.parse import ParseCommandException
from avabot.constants import DEFAULT_CLASS, DEFAULT_HITL


class Parser:
    def run(self, message, channel, user):
        raise NotImplementedError


class MessageParser(Parser):
    __doc__ = """Ava Slackbot

Usage:
    @ava (fo|find-object) <urls>... [-pc] [--class=<class>] [--model=<model_id>] [--hitl=<hitl>] [-r|--raw-json]
    @ava (foc|find-object-consensus) <urls>... [-pc] [--class=<class>] [-r|--raw-json]
    @ava (ft|find-target) <urls>... --target=<target> [-r|--raw-json]
    @ava (gft|get-find-target) <job_id> [-r|--raw-json]
    @ava (-h|--help|-v|--version)

Commands:
    (fo|find-object)             request against /find-object
    (foc|find-object-consensus)  multiple requests for multiple modules against /find-object

Arguments:
    <urls>...         image urls you want to run detections on
    <model_id>        the model id you want to perform classification against

Options:
    -h --help         shows this
    -v --version      shows version

    -p                person class (default)
    -c                car class
    --class=<class>   specify the class you want to find in the url

    -r --raw-json     returns the raw JSON response from the Image Intelligence API
    --hitl=<hitl>     additional verification (AUTO, ALWAYS, NEVER) [default: %s]

Author: %s <%s>, Image Intelligence
GitHub: https://github.com/ImageIntelligence/ava-slackbot
API: https://docs.imageintelligence.com""" % (
        DEFAULT_HITL,
        __author__,
        __author_email__
    )

    def run(self, message, channel, user):
        filtered_message = shlex.split(message)[1:]
        filtered_message = map(lambda i: i.strip('<>'), filtered_message)
        filtered_message = list(filtered_message)

        slack_data = {'channel': channel, 'user': user}
        try:
            arguments = docopt.docopt(MessageParser.__doc__, filtered_message, help=False, version=False)
        except docopt.DocoptExit as e:
            raise ParseCommandException(str(e))

        if any((m in ('-h', '--help')) and m for m in filtered_message):
            parsed_data = {'--extras': MessageParser.__doc__, **arguments}
        elif any((m in ('-v', '--version')) and m for m in filtered_message):
            parsed_data = {'--extras': 'Ava Slackbot v%s' % __version__, **arguments}
        else:
            parsed_data = arguments
        return {**slack_data, **parsed_data}
