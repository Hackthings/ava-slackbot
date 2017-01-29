# -*- coding: utf-8 -*-
import requests

from StringIO import StringIO
from PIL import Image, ImageDraw
from slackbot.bot import settings

from avabot.utils.constants import CLASS_COLOR_MAP
from avabot.vendor.pil_extensions import draw_detection_region
from avabot.vendor.aws import s3, s3_client


def download_image(url):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return None
    return Image.open(StringIO(response.content))


def upload_image(image, name, acl='public-read', encoding='JPEG', expires_in=31536000):
    output_image = StringIO()
    image.save(output_image, encoding, optimize=True, quality=95)

    bucket = s3.Bucket(settings.S3_RESULTS_BUCKET)
    s3_object = bucket.put_object(
        ACL=acl,
        Body=output_image.getvalue(),
        Key='detections/%s.%s' % (name, encoding.lower())
    )
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.S3_RESULTS_BUCKET, 'Key': s3_object.key},
        ExpiresIn=expires_in  # expire after 1 year.
    )
    return s3_object, url


def draw_bounding_boxes(
    image, objects, ignore_min_confidence=settings.MIN_CONFIDENCE, color_map=CLASS_COLOR_MAP
):
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

        draw_detection_region(draw, pos, label, color_map[obj['class']])
    return image
