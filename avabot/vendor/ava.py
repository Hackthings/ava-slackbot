# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
import requests
import datetime
import time
import logging


class AvaAPIAuth(object):
    AUTH_TOKEN_REFRESH_THRESHOLD = 1000 * 30  # 0.5 minutes in milliseconds

    def __init__(self, client_id, client_secret, endpoint, version):
        self.client_id = client_id
        self.client_secret = client_secret
        self.endpoint = endpoint
        self.version = version
        self._auth = {}

    def is_expired(self):
        if not self._auth:
            return True

        now = int(datetime.datetime.now().strftime('%s')) * 1000
        return now >= (self._auth['expires_at'] - self.__class__.AUTH_TOKEN_REFRESH_THRESHOLD)

    def request_new_token(self):
        auth_endpoint = os.path.join(self.endpoint, self.version, 'oauth/token')
        payload = {'clientId': self.client_id, 'clientSecret': self.client_secret}

        response = requests.post(auth_endpoint, data=json.dumps(payload))
        if response.status_code != 200:
            return False

        response_payload = response.json()

        self._auth['token'] = response_payload['accessToken']
        self._auth['expires_at'] = response_payload['expiresAt']
        self._auth['issued_at'] = response_payload['issuedAt']
        self._auth['org_name'] = response_payload['orgName']
        return True

    @property
    def token(self):
        if self.is_expired():
            logging.debug('token is expired, refreshing token')
            self.request_new_token()
        return self._auth['token']


class AvaAPI(object):
    ERROR_STATUSES = ['PARTIAL_ERROR', 'ERROR']
    IN_PROGRESS_STATUS = 'IN_PROGRESS'

    def __init__(self, client_id, client_secret, endpoint, version):
        self.auth = AvaAPIAuth(client_id, client_secret, endpoint, version)

        self.endpoint = endpoint
        self.version = version

    def _api_request(self, method, endpoint, payload=None, headers=None):
        payload = payload or {}
        headers = headers or {}

        token = self.auth.token
        if not token:
            return None

        headers['Authorization'] = 'Bearer %s' % token
        response = method(endpoint, data=json.dumps(payload), headers=headers)
        logging.debug('received response code: %s (%s)' % (response.status_code, endpoint))

        return response.json() if response.status_code == 200 else None

    def detect(self, url, webhook_url):
        payload = {
            'items': [{'url': url}], 'webhookUrl': webhook_url,
        }
        endpoint = os.path.join(self.endpoint, self.version, 'detect')
        headers = {
            'Content-Type': 'application/json',
        }

        response = self._api_request(requests.post, endpoint, payload, headers)
        return response['id'] if response is not None else None

    def get_image_result(self, job_id):
        endpoint = os.path.join(self.endpoint, self.version, 'detect', job_id)
        response = self._api_request(requests.get, endpoint)
        return response if response is not None else {}

    def poll_until_complete(self, job_id):
        tag_result = self.get_image_result(job_id)
        while tag_result and tag_result['status']['code'] == self.__class__.IN_PROGRESS_STATUS:
            tag_result = self.get_image_result(job_id)
            logging.info('status for "%s": %s' % (job_id, tag_result.get('status', 'N/A')))
            time.sleep(0.5)

        if not tag_result or tag_result['status']['code'] in self.__class__.ERROR_STATUSES:
            return None
        return tag_result
