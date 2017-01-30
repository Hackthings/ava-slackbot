# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import re

from slackbot.bot import respond_to

from avabot.vendor.ava import tag_image
from avabot.vendor.ava import poll_until_complete

from utils.image_processing import download_image, upload_image
from utils.image_processing import draw_bounding_boxes


@respond_to('tag <(.*)>', re.IGNORECASE)
def tag(message, url):
    print('[debug] received url from client "%s"' % url)

    job_id = tag_image(url, 'https://www.google.com/')
    if not job_id:
        return message.reply('Ava died... something went wrong')

    print('[debug] polling for result until done')
    tag_result = poll_until_complete(job_id)
    if tag_result is None or tag_result['status']['code'] != 'COMPLETED_SUCCESSFULLY':
        return message.reply('Ava died... something went wrong')

    print('[debug] download image')
    image = download_image(url)
    if not image:
        return message.reply('Ava failed to the image "%s"' % url)

    # we're only ever pushing one url at a time.
    print('[debug] drawing bounding on objects in image')
    image = draw_bounding_boxes(image, tag_result['results'][0]['objects'])

    print('[debug] uploading images to storage')
    _, name = os.path.split(url)
    name, _ = os.path.splitext(name)
    _, image_url = upload_image(image, name)
    message.reply(image_url)

    print('[debug] done')
