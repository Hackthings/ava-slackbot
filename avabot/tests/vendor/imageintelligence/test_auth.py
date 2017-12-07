# -*- coding: utf-8 -*-
import pytest

from avabot.tests import config
from avabot.exceptions.imageintelligence import InvalidClientCredentialsError
from avabot.exceptions.imageintelligence import UnknownAuthenticationError
from avabot.vendor.imageintelligence.auth import get_token


class TestGetToken:
    client_id = config.api_client_id
    client_secret = config.api_client_secret
    endpoint = config.api_endpoint

    def test_new_token_generated_with_valid_credentials(self):
        token = get_token(self.client_id, self.client_secret, base_endpoint=self.endpoint)
        assert token

    def test_invalid_client_credentials_causes_an_error(self):
        with pytest.raises(InvalidClientCredentialsError):
            get_token('invalid_id', 'invalid_secret', base_endpoint=self.endpoint)

    def test_unexpected_auth_errors_causes_an_error(self):
        with pytest.raises(UnknownAuthenticationError):
            get_token(None, 'invalid_secret', base_endpoint=self.endpoint)
        with pytest.raises(UnknownAuthenticationError):
            get_token('invalid_id', None, base_endpoint=self.endpoint)
        with pytest.raises(UnknownAuthenticationError):
            get_token(None, None, base_endpoint=self.endpoint)
