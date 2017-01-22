# -*- coding: utf-8 -*-
import requests
from StringIO import StringIO
from PIL import Image, ImageDraw


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

        box_pos = [x_min, y_min, x_max, y_max]
        for i in xrange(2):
            draw.rectangle(box_pos, outline='red')
            box_pos = [c + 1 for c in box_pos]

        label = '%s %.4f' % (detection_class, confidence)
        label_pos = [x_min + 4, y_max - 12]  # add padding to make text visible.
        draw.text(label_pos, label, fill='red')
    return image
