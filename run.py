# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import logging

from slackbot.bot import Bot
from slackbot.bot import settings

from avabot.config import Config
from avabot.vendor.ava import AvaAPI


def main():
    logging.basicConfig(level=logging.DEBUG)

    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)

    logging.info('loading configuration variables')

    config = Config(os.path.join(os.path.dirname(__file__), '.env'))
    config.load()

    ava_client = AvaAPI(
        config.get('AVA_CLIENT_ID'),
        config.get('AVA_CLIENT_SECRET'),
        config.get('AVA_API_ENDPOINT'),
        config.get('AVA_API_VERSION')
    )

    settings.PLUGINS = [
        'avabot.plugins',
    ]
    settings.API_TOKEN = config.get('SLACK_API_TOKEN')
    settings.config = config
    settings.ava_client = ava_client

    bot = Bot()
    logging.info('ava-slackbot running. ready to accept messages')
    bot.run()

if __name__ == '__main__':
    main()
