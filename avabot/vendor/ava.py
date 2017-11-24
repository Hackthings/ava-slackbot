# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import time

from http import HTTPStatus
import requests

from avabot.domain.exceptions.ava import AvaInvalidTokenException


class AvaApiAuth:
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
        if response.status_code != HTTPStatus.OK:
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
            self.request_new_token()
        return self._auth['token']


class AvaApi:
    ERROR_STATUSES = ['PARTIAL_ERROR', 'ERROR']
    IN_PROGRESS_STATUS = 'IN_PROGRESS'

    def __init__(self, client_id, client_secret, endpoint, version):
        self.auth = AvaApiAuth(client_id, client_secret, endpoint, version)

        self.endpoint = endpoint
        self.version = version

    def _api_request(self, method, endpoint, payload=None, headers=None):
        payload = payload or {}
        headers = headers or {}

        token = self.auth.token
        if not token:
            raise AvaInvalidTokenException('failed to retrieve ava api token')

        headers['Authorization'] = 'Bearer %s' % token
        response = method(endpoint, data=json.dumps(payload), headers=headers)
        logging.info('received response code: %s (%s)' % (response.status_code, endpoint))

        if response.status_code >= 500:
            return {
                'body': {'error': response.text},
                'code': response.status_code,
            }
        return {
            'body': response.json(),
            'code': response.status_code,
        }

    def detect(self, url, model=None, version=None):
        payload = {'items': [{'url': url}]}
        if model is not None:
            payload['model'] = model
        if model and version:
            payload['model'] = {'name': model, 'version': version}

        endpoint = os.path.join(self.endpoint, self.version, 'detect')
        headers = {'Content-Type': 'application/json'}

        return self._api_request(requests.post, endpoint, payload, headers)

    def get_image_result(self, job_id):
        endpoint = os.path.join(self.endpoint, self.version, 'detect', job_id)
        return self._api_request(requests.get, endpoint)

    def _should_continue_poll(self, response):
        body = response['body']
        status_code = response['code']
        if status_code != HTTPStatus.OK:
            return False

        job_status_code = body['results'][0]['status']['code']
        return job_status_code == self.__class__.IN_PROGRESS_STATUS

    def poll_until_complete(self, job_id):
        response = self.get_image_result(job_id)

        while self._should_continue_poll(response):
            logging.info('polling for job (%s) to complete' % job_id)
            response = self.get_image_result(job_id)
            time.sleep(0.5)
        return response
