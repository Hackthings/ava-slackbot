#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from typing import Dict
from functools import partial

from avabot.config import Config, load as load_config
from avabot.vendor.slack import Slack
from avabot.services.parsers import MessageParser


def handle_message(client: Slack, config: Config, arguments: Dict) -> None:
    if '--extras' in arguments:
        client.send_message('\n'.join([
            '<@%s> See `--help` usage or `--version` below:' % arguments['user'],
            '```',
            arguments['--extras'],
            '```',
        ]).strip('\n'), arguments['channel'])
    else:
        logging.info(arguments)
    return None


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('init ava-slackbot!')

    config = load_config()
    slack = Slack(config.slack, MessageParser())
    slack.listen(partial(handle_message, slack, config))

if __name__ == '__main__':
    main()
