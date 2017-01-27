# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import os

from slackbot.bot import Bot
from slackbot.bot import settings

from dotenv import load_dotenv


def main():
    logging.basicConfig()

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    settings.AVA_API_ENDPOINT = 'http://' + os.environ['AVA_API_ENDPOINT']
    settings.API_TOKEN = os.environ['SLACK_API_TOKEN']
    settings.MIN_CONFIDENCE = float(os.environ['MIN_CONFIDENCE'])
    settings.AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    settings.AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    settings.S3_RESULTS_BUCKET = os.environ['S3_RESULTS_BUCKET']

    settings.PLUGINS = [
        'avabot.plugins',
    ]

    bot = Bot()
    print('bot running... ready to accept messages')
    bot.run()

if __name__ == '__main__':
    main()
