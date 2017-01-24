# -*- coding: utf-8 -*-
import requests
from StringIO import StringIO
from PIL import Image, ImageDraw

from avabot.vendor.pil_extensions import draw_detection_region


def download_image(url):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return None
    return Image.open(StringIO(response.content))


def draw_bounding_boxes(image, objects):
    draw = ImageDraw.Draw(image)
    for obj in objects:
        bounding_box = obj['boundingBox']
        confidence = obj['confidence']
        detection_class = obj['class']

        x_min = bounding_box['xMin']
        y_min = bounding_box['yMin']
        x_max = bounding_box['xMax']
        y_max = bounding_box['yMax']

        pos = [x_min, y_min, x_max, y_max]
        label = '%s %.4f' % (detection_class, confidence)

        draw_detection_region(draw, pos, label, 'red')
    return image
