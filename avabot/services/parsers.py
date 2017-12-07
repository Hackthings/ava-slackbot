# -*- coding: utf-8 -*-
import shlex

import docopt

from avabot import __author__, __author_email__
from avabot import __version__
from avabot.exceptions.parse import ParseCommandException


class Parser:
    def run(self, message, channel, user):
        raise NotImplementedError


class MessageParser(Parser):
    __doc__ = """Ava Slackbot

Usage:
    @ava (d|detect) <url> [--raw-json]
    @ava (-h|--help|-v|--version)

Commands:
    (d|detect)    request against /v1/detect

Arguments:
    <url>         image url you want to run detections on
    <id>          a job id or custom id to search against

Options:
    -h --help     shows this
    -v --version  shows version

    -a --all      shows all objects the NN model returned
    -raw-json     returns the raw JSON response from the Image Intelligence API

Author: %s <%s>, Image Intelligence
GitHub: https://github.com/ImageIntelligence/ava-slackbot
API: https://imageintelligence.com/docs""" % (__author__, __author_email__)

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
