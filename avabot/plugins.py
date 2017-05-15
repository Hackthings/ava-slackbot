# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import re
import logging

from slackbot import settings
from slackbot.bot import respond_to
from avabot.vendor.slack import should_respond_to_message

config = settings.config
client = settings.ava_client
DEFAULT_WEBHOOK_URL = 'https://www.google.com/'


@respond_to('detect <(.*)>', re.IGNORECASE)
def detect(message, url):
    channel_id = message.body['channel']

    logging.info('received url from client (%s) "%s"' % (channel_id, url))
    if not should_respond_to_message(message):
        logging.warning('not responding to slack message')
        return message.reply('No soup for you')

    job_id = client.detect(url, DEFAULT_WEBHOOK_URL)
    if not job_id:
        logging.error('failed to tag image %s' % url)
        return message.reply('Ava died... something went wrong')

    logging.info('polling for result until done')
    tag_result = client.poll_until_complete(job_id)
    if tag_result is None or tag_result['status']['code'] != 'COMPLETED_SUCCESSFULLY':
        status = tag_result['status']

        logging.error('polling complete found api error')
        return message.reply('%s: %s' % (status['code'], status['message']))

    message.reply(json.dumps(tag_result))
    logging.info('finished performing detection')
