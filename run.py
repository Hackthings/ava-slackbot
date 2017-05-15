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
from avabot.vendor.ava import AvaApi
from avabot.domain import AvaSlackbotException


def handle_message(
    slack_client: Slack,
    ava_client: AvaApi,
    config: Config,
    arguments: Dict
) -> None:
    try:
        if '--extras' in arguments:
            slack_client.send_formatted_message(
                'See `--help` usage or `--version` below:',
                arguments['--extras'],
                arguments['channel'],
                arguments['user']
            )
        elif arguments['detect']:
            Detect(config, ava_client, slack_client, **arguments)
        else:
            logging.info(arguments)
    except AvaSlackbotException as e:
        if isinstance(e.message, dict):
            error_message = json.dumps(e.message, indent=2, sort_keys=True)
        else:
            error_message = str(e)

        slack_client.send_formatted_message(
            'An error has occurred processing your request...',
            error_message,
            arguments['channel'],
            arguments['user']
        )
    return None


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
