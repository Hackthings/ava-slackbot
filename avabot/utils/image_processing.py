# -*- coding: utf-8 -*-
import requests

from StringIO import StringIO
from PIL import Image, ImageDraw
from slackbot.bot import settings

from avabot.vendor.pil_extensions import draw_detection_region


def download_image(url):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return None
    return Image.open(StringIO(response.content))


def draw_bounding_boxes(image, objects, ignore_min_confidence=settings.MIN_CONFIDENCE):
    draw = ImageDraw.Draw(image)
    for obj in objects:
        if obj['confidence'] < ignore_min_confidence:
            continue
        bounding_box = obj['boundingBox']
        x_min = bounding_box['xMin']
        y_min = bounding_box['yMin']
        x_max = bounding_box['xMax']
        y_max = bounding_box['yMax']

        pos = [x_min, y_min, x_max, y_max]
        label = '%s %.4f' % (obj['class'], obj['confidence'])

        draw_detection_region(draw, pos, label, 'red')
    return image
