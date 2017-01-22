# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import time

from slackbot.bot import respond_to

from avabot.vendor.ava import tag_image
from avabot.vendor.ava import get_image_result

from utils.image_processor import download_image
from utils.image_processor import draw_bounding_boxes


@respond_to('tag <(.*)>', re.IGNORECASE)
def tag(message, url):
    job_id = tag_image(url)
    if not job_id:
        message.reply('Ava died... something went wrong')
        return

    tag_result = get_image_result(job_id)
    while tag_result and tag_result['status']['code'] == 'IN_PROGRESS':
        tag_result = get_image_result(job_id)
        time.sleep(1)

    if not tag_result or tag_result['status']['code'] in ['PARTIAL_ERROR', 'ERROR']:
        message.reply('Ava died... something went wrong')
    else:
        image = download_image(url)
        if not image:
            message.reply('Ava failed to the image "$s"' % url)
            return
        image = draw_bounding_boxes(image, tag_result['results'][0]['objects'])
        image.save('test_output.png', 'PNG')
        message.reply('Ava tagged and saved image')
