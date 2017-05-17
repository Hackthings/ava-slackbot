#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json

from typing import Dict
from functools import partial

from avabot.config import Config, load as load_config
from avabot.vendor.slack import Slack
from avabot.services.parsers import MessageParser

from avabot.commands.detect import Detect
from avabot.commands.consensus import Consensus
from avabot.vendor.ava import AvaApi
from avabot.domain import AvaSlackbotException


def send_error_message(slack_client, error_message, arguments):
    slack_client.send_formatted_message(
        'An error has occurred processing your request...',
        error_message,
        arguments['channel'],
        arguments['user']
    )


def handle_message(
    slack_client: Slack,
    ava_client: AvaApi,
    config: Config,
    arguments: Dict
) -> None:
    try:
        # checking for the value of the argument
        if arguments['--top']:
            try:
                arguments['--top'] = int(arguments['--top'])
            except ValueError:
                raise ValueError('--top: number of top categories must be a valid integer')

            if arguments['--top'] <= 0:
                raise ValueError('--top: number of top categories must be greater than 0')

        if '--extras' in arguments:
            slack_client.send_formatted_message(
                'See `--help` usage or `--version` below:',
                arguments['--extras'],
                arguments['channel'],
                arguments['user']
            )
        elif arguments['detect']:
            Detect(config, ava_client, slack_client, **arguments)
        elif arguments['consensus']:
            Consensus(config, ava_client, slack_client, **arguments)
        elif arguments['find-person']:
            slack_client.send_message('`find-person` not yet implemented :cry:', arguments['channel'])
        elif arguments['search']:
            slack_client.send_message('`search` not yet implemented :cry:', arguments['channel'])
        else:
            logging.error('unexpected arguments %s' % arguments)
    except AvaSlackbotException as e:
        if isinstance(e.message, dict):
            error_message = json.dumps(e.message, indent=2, sort_keys=True)
        else:
            error_message = str(e)

        send_error_message(slack_client, error_message, arguments)
    except ValueError as e:
        send_error_message(slack_client, str(e), arguments)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('init ava-slackbot!')

    config = load_config()
    ava_client = AvaApi(
        config.ava.client_id,
        config.ava.client_secret,
        config.ava.endpoint,
        config.ava.version
    )

    slack_client = Slack(config.slack, MessageParser())
    slack_client.listen(partial(handle_message, slack_client, ava_client, config))

if __name__ == '__main__':
    main()
