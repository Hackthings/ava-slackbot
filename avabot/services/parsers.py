# -*- coding: utf-8 -*-
import shlex
from typing import Dict

import docopt

from ..domain.exceptions.parse import ParseCommandException
from .. import __author__, __author_email__
from .. import __version__


class Parser:
    def run(self, message: str, channel: str, user: str) -> None:
        raise NotImplementedError


class MessageParser(Parser):
    __doc__ = """Ava Slackbot

Usage:
    @ava consensus <url> [--raw-json] [--all] [--top=<top>] [--mean]
    @ava detect <url> [--model=<model>] [--raw-json] [--top=<top>]
    @ava find-person <url> [--model=<model>] [--raw-json]
    @ava search <id>
    @ava (-h|--help|-v|--version)

Commands:
    consensus        makes a request against the /v1/detect endpoint over all available models
    detect           makes a request against the /v1/detect endpoint
    find-person      makes a request against the /v1/find-person endpoint
    search           performs a search for the given <custom_id>

Arguments:
    <url>            image url you want to run detections on
    <id>             a job id or custom id to search against

Options:
    -h --help        shows this
    -v --version     shows version

    --all            shows all objects the NN model returned
    --mean           shows the average confidence of all models (does not work with --all)
    --top=<top>      truncates to the top number of objects returned
    --model=<model>  the NN model to run detections with
    --raw-json       returns the raw JSON response from the Image Intelligence API

Author: %s <%s>, Image Intelligence
GitHub: https://github.com/ImageIntelligence/ava-slackbot
API: https://imageintelligence.com/docs""" % (__author__, __author_email__)

    def run(self, message: str, channel: str, user: str) -> Dict:
        filtered_message = shlex.split(message)[1:]
        filtered_message = map(lambda i: i.strip('<>'), filtered_message)
        filtered_message = list(filtered_message)

        slack_data = {'channel': channel, 'user': user}
        try:
            arguments = docopt.docopt(MessageParser.__doc__, filtered_message, help=False, version=False)
        except docopt.DocoptExit as e:
            raise ParseCommandException(e)

        if any((m in ('-h', '--help')) and m for m in filtered_message):
            parsed_data = {'--extras': MessageParser.__doc__}
        elif any((m in ('-v', '--version')) and m for m in filtered_message):
            parsed_data = {'--extras': 'Ava Slackbot v%s' % __version__}
        else:
            parsed_data = arguments
        return {**slack_data, **parsed_data}
