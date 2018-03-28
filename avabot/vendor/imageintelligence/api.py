# -*- coding: utf-8 -*-
import json
import requests
import time
from http import HTTPStatus

from avabot.vendor.imageintelligence.auth import get_token
from avabot.vendor.imageintelligence import BASE_ENDPOINT

from avabot.exceptions.imageintelligence import ApiRequestError, ApiRequestTimeoutError
from avabot.constants import MAX_POLL_ATTEMPTS


class ImageIntelligenceApi:

    def __init__(self, client_id, client_secret, base_endpoint=BASE_ENDPOINT, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_endpoint = base_endpoint
        self.token = token

    def refresh_token(self):
        if self.token and not self.token.expired:
            return self.token
        self.token = get_token(
            self.client_id,
            self.client_secret,
            base_endpoint=self.base_endpoint,
        )
        return self.token

    def api_request(self, method, endpoint, token, payload=None, headers=None):
        payload = payload or {}
        headers = headers or {}

        headers['Authorization'] = 'Bearer %s' % token.token
        response = method(endpoint, data=json.dumps(payload), headers=headers)

        if response.status_code != HTTPStatus.OK:
            raise ApiRequestError('(%s) %s' % (response.status_code, response.text))
        return response.json()

    def detect(self, images, classes, webhook_url=None, feed_id=None, custom_id=None):
        return self.api_request(
            requests.post,
            self.base_endpoint + '/detect',
            self.refresh_token(),
            payload={
                'images': images,
                'classes': classes,
                'webhookUrl': webhook_url,
                'feedId': feed_id,
                'customId': custom_id,
            },
        )

    def match(self, images, target, webhook_url=None, feed_id=None, custom_id=None):
        return self.api_request(
            requests.post,
            self.base_endpoint + '/match',
            self.refresh_token(),
            payload={
                'images': images,
                'target': target,
                'webhookUrl': webhook_url,
                'feedId': feed_id,
                'customId': custom_id,
            },
        )

    def ask(self, images, question, webhook_url=None, feed_id=None, custom_id=None):
        return self.api_request(
            requests.post,
            self.base_endpoint + '/ask',
            self.refresh_token(),
            payload={
                'images': images,
                'question': question,
                'webhookUrl': webhook_url,
                'feedId': feed_id,
                'customId': custom_id,
            },
        )

    def video(self, video, fps, classes, webhook_url=None, feed_id=None, custom_id=None):
        return self.api_request(
            requests.post,
            self.base_endpoint + '/video',
            self.refresh_token(),
            payload={
                'video': video,
                'classes': classes,
                'fps': fps,
                'webhookUrl': webhook_url,
                'feedId': feed_id,
                'customId': custom_id,
            },
        )

    def get_job(self, path, job_id):
        return self.api_request(
            requests.get,
            self.base_endpoint + path + '/' + job_id,
            self.refresh_token(),
        )

    def get_detect_job(self, job_id):
        return self.get_job('/detect', job_id)

    def get_match_job(self, job_id):
        return self.get_job('/match', job_id)

    def get_ask_job(self, job_id):
        return self.get_job('/ask', job_id)

    def get_video_job(self, job_id):
        return self.get_job('/ask', job_id)

    def poll_for_job_result(self, path, job_id, attempts):
        endpoint = self.base_endpoint + path + '/' + job_id
        for _ in range(attempts):
            response = self.api_request(
                requests.get,
                endpoint,
                self.refresh_token(),
            )
            if response['status'] != 'IN_PROGRESS':
                return response
            time.sleep(0.5)
        raise ApiRequestTimeoutError('polling for job results took too long - jobId=%s' % response['id'])

    def poll_for_match_result(self, job_id, attempts=MAX_POLL_ATTEMPTS):
        return self.poll_for_job_result('/match', job_id, attempts)

    def poll_for_detect_result(self, job_id, attempts=MAX_POLL_ATTEMPTS):
        return self.poll_for_job_result('/detect', job_id, attempts)

    def poll_for_video_result(self, job_id, attempts=MAX_POLL_ATTEMPTS):
        return self.poll_for_job_result('/video', job_id, attempts)
