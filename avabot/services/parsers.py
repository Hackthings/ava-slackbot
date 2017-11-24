# -*- coding: utf-8 -*-
import shlex
import docopt

from ..domain.exceptions.parse import ParseCommandException
from .. import __author__, __author_email__
from .. import __version__


class Parser:
    def run(self, message, channel, user):
        raise NotImplementedError


class MessageParser(Parser):
    __doc__ = """Ava Slackbot

Usage:
    @ava (c|consensus) <url> [--raw-json] [--all] [--head=<n>]
    @ava (d|detect) <url> [--model=<model> --mversion=<version>] [--raw-json] [--head=<n>]
    @ava (fp|find-person) <url> [--model=<model>] [--raw-json]
    @ava (s|search) <id>
    @ava (-h|--help|-v|--version)

Commands:
    (c|consensus)         request against /v1/detect over all available models (except beta)
    (d|detect)            request against /v1/detect
    (fp|find-person)      request against /v1/find-person
    (s|search)            performs a search for the given <custom_id>

Arguments:
    <url>                 image url you want to run detections on
    <id>                  a job id or custom id to search against

Options:
    -h --help             shows this
    -v --version          shows version

    -a --all              shows all objects the NN model returned
    --head=<n>            truncates to the top number of objects returned
    --model=<model>       the NN model to run detections with
    --mversion<=version>  the version uuid for the given --model

    -raw-json             returns the raw JSON response from the Image Intelligence API

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
