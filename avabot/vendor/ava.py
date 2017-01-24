# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
import requests

from slackbot.bot import settings


def tag_image(url):
    payload = json.dumps({
        'items': [{'url': url}],
        'webhookUrl': 'http://www.google.com/',
    })
    endpoint = os.path.join(settings.AVA_API_ENDPOINT, 'tag')
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(endpoint, data=payload, headers=headers)
    return response.json()['id'] if response.status_code == 200 else None


def get_image_result(id):
    endpoint = os.path.join(settings.AVA_API_ENDPOINT, 'tag', id)
    response = requests.get(endpoint)
    return response.json() if response.status_code == 200 else None
