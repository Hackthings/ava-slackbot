# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
import requests
import time

from slackbot.bot import settings


def tag_image(url, webhook_url):
    payload = json.dumps({
        'items': [{'url': url}], 'webhookUrl': webhook_url,
    })
    endpoint = os.path.join(settings.AVA_API_ENDPOINT, 'tag')
    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(endpoint, data=payload, headers=headers)
    return response.json()['id'] if response.status_code == 200 else None


def get_image_result(job_id):
    endpoint = os.path.join(settings.AVA_API_ENDPOINT, 'tag', job_id)
    response = requests.get(endpoint)
    return response.json() if response.status_code == 200 else None


def poll_until_complete(job_id):
    tag_result = get_image_result(job_id)
    while tag_result and tag_result['status']['code'] == 'IN_PROGRESS':
        tag_result = get_image_result(job_id)
        print(tag_result['status'])
        time.sleep(0.5)

    if not tag_result or tag_result['status']['code'] in ['PARTIAL_ERROR', 'ERROR']:
        return None
    return tag_result
