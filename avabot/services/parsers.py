# -*- coding: utf-8 -*-
import logging
import shlex
import docopt

from typing import Dict

from ..domain.parse_exceptions import ParseCommandException


class Parser:
    def run(self, message: str, channel: str, user: str) -> None:
        raise NotImplementedError


class MessageParser(Parser):
    __doc__ = """Ava Slackbot

usage:
    @ava detect <url> [--model=<model>] [--raw-json]
    @ava find-person <url> [--model=<model>] [--raw-json]
    @ava search <id>

commands:
    detect           makes a request against the /v1/detect endpoint
    find-person      makes a request against the /v1/find-person endpoint
    search           performs a search for the given <custom_id>

arguments:
    <url>            image url you want to run detections on
    <id>             a job id or custom id to search against

options:
    -h --help        shows this
    -v --version     shows version

    --model=<model>  the NN model to run detections with
    --raw-json       returns the raw JSON response from the Image Intelligence API

    """

    def run(self, message: str, channel: str, user: str) -> Dict:
        filtered_message = shlex.split(message)[1:]
        filtered_message = map(lambda i: i.strip('<>'), filtered_message)
        filtered_message = list(filtered_message)

        try:
            return docopt.docopt(MessageParser.__doc__, filtered_message)
        except docopt.DocoptExit as e:
            raise ParseCommandException(e)
