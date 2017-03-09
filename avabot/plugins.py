# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import re
import logging

from slackbot import settings
from slackbot.bot import respond_to

from avabot.vendor.slack import should_respond_to_message

from utils.image_processing import download_image, upload_image
from utils.image_processing import draw_bounding_boxes

config = settings.config
client = settings.ava_client
DEFAULT_WEBHOOK_URL = 'https://www.google.com/'


@respond_to('detect <(.*)>', re.IGNORECASE)
def detect(message, url):
    logging.info('received url from client "%s"' % url)
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
        return message.reply('Ava died... something went wrong')

    logging.info('downloading image %s' % url)
    image = download_image(url)
    if not image:
        logging.error('failed to download image %s' % url)
        return message.reply('Ava failed to the image "%s"' % url)

    # we're only ever pushing one url at a time.
    logging.info('drawing bounding on objects in image')
    image = draw_bounding_boxes(image, tag_result['results'][0]['objects'])

    logging.info('uploading images to s3 for storage')
    _, name = os.path.split(url)
    name, _ = os.path.splitext(name)
    _, image_url = upload_image(image, name)
    message.reply(image_url)

    logging.info('finished performing detection')
