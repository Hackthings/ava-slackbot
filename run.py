#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
from functools import partial

from avabot.commands.find_object import FindObject
from avabot.commands.get_find_object import GetFindObject
from avabot.commands.find_target import FindTarget
from avabot.commands.get_find_target import GetFindTarget
from avabot.commands.find_object_consensus import FindObjectConsensus
from avabot.config import load as load_config
from avabot.exceptions import AvaSlackbotException
from avabot.services.parsers import MessageParser
from avabot.vendor.slack import Slack
from avabot.vendor.imageintelligence.api import ImageIntelligenceApi


def send_error_message(slack_client, error_message, arguments):
    slack_client.send_formatted_message(
        'An error has occurred processing your request...',
        error_message,
        arguments['channel'],
        arguments['user']
    )


def handle_message(slack_client, ii_client, config, args):
    try:
        if '--extras' in args:
            slack_client.send_formatted_message(
                'See `--help` usage or `--version` below:',
                args['--extras'],
                args['channel'],
                args['user']
            )
        elif any([args['fo'], args['find-object']]):
            FindObject(config, ii_client, slack_client, **args)
        elif any([args['gfo'], args['get-find-object']]):
            GetFindObject(config, ii_client, slack_client, **args)
        elif any([args['foc'], args['find-object-consensus']]):
            FindObjectConsensus(config, ii_client, slack_client, **args)
        elif any([args['ft'], args['find-target']]):
            FindTarget(config, ii_client, slack_client, **args)
        elif any([args['gft'], args['get-find-target']]):
            GetFindTarget(config, ii_client, slack_client, **args)
        else:
            logging.error('unexpected args %s' % args)
    except AvaSlackbotException as e:
        if isinstance(e.message, dict):
            error_message = json.dumps(e.message, indent=2, sort_keys=True)
        else:
            error_message = str(e)

        send_error_message(slack_client, error_message, args)
    except ValueError as e:
        send_error_message(slack_client, str(e), args)


def main():
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    ii_client = ImageIntelligenceApi(
        config.ii.client_id,
        config.ii.client_secret,
        config.ii.endpoint,
    )

    slack_client = Slack(config.slack, MessageParser())
    slack_client.listen(partial(handle_message, slack_client, ii_client, config))


if __name__ == '__main__':
    main()
