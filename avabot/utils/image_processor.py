# -*- coding: utf-8 -*-
import urllib
import cStringIO

from PIL import Image, ImageDraw

FONT_PADDING_LEFT = 5
FONT_PADDING_BOTTOM = 12


def download_image(url):
    file = cStringIO.StringIO(urllib.urlopen(url).read())
    return Image.open(file)


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

        draw.rectangle([x_min, y_min, x_max, y_max])

        label = '%s %s' % (detection_class, confidence)
        draw.text(
            [x_min + FONT_PADDING_LEFT, y_max - FONT_PADDING_BOTTOM], label
        )
    return image
