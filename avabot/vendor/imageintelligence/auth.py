# -*- coding: utf-8 -*-
import time
import json
from http import HTTPStatus

import requests

from avabot.exceptions.imageintelligence import UnknownAuthenticationError
from avabot.exceptions.imageintelligence import InvalidClientCredentialsError
from avabot.vendor.imageintelligence import BASE_ENDPOINT, OAUTH_PATH


class ImageIntelligenceApiToken:
    AUTH_TOKEN_EXPIRE_BUFFER = 1000 * 30  # 0.5 minutes in milliseconds

    def __init__(self, **kwargs):
        self.token = kwargs['accessToken']
        self.expires_at = kwargs['expiresAt']
        self.issued_at = kwargs['issuedAt']
        self.org_name = kwargs['orgName']
        self.app_name = kwargs['appName']
        self.scope = kwargs['scope']

    @property
    def expired(self):
        return (time.time() * 1000) >= (self.expires_at - self.AUTH_TOKEN_EXPIRE_BUFFER)


def get_token(client_id, client_secret, base_endpoint=BASE_ENDPOINT):
    endpoint = base_endpoint + OAUTH_PATH
    payload = {'clientId': client_id, 'clientSecret': client_secret}

    response = requests.post(endpoint, data=json.dumps(payload))
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise InvalidClientCredentialsError()
    if response.status_code != HTTPStatus.OK:
        raise UnknownAuthenticationError()
    return ImageIntelligenceApiToken(**response.json())
