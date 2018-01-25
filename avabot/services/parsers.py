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
    @ava (fo|find-object) <urls>... [(--class=<class>)...] [--model=<model_id>] [--hitl=<hitl>] [--raw-json]
    @ava (gfo|get-find-object) <job_id> [--raw-json]
    @ava (foc|find-object-consensus) <urls>... [(--class=<class>)...] [--raw-json]
    @ava (ft|find-target) <urls>... (--target=<target>)... [--raw-json]
    @ava (gft|get-find-target) <job_id> [--raw-json]
    @ava (--help|--version)

Arguments:
    <urls>...              image urls (space separated) you want to run detections on
    <job_id>               job id

Options:
    -c --class=<class>     specify the class you want to find in the url
    -m --model=<model_id>  specify model to use
    -t --target=<target>   target image urls for ft requests
    -l --hitl=<hitl>       additional verification for fo requests (AUTO, ALWAYS, NEVER) [default: %s]
    -r --raw-json          returns the raw JSON response from the Image Intelligence API
    -h --help              shows this
    -v --version           shows version

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
