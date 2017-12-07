# -*- coding: utf-8 -*-
import pytest

from avabot.tests import config
from avabot.tests.generators import gen_random_string
from avabot.vendor.imageintelligence.auth import get_token
from avabot.vendor.imageintelligence.api import ImageIntelligenceApi
from avabot.exceptions.imageintelligence import ApiRequestError


class TestImageIntelligenceApiFindObject:
    client_id = config.api_client_id
    client_secret = config.api_client_secret
    base_endpoint = config.api_endpoint
    token = get_token(client_id, client_secret, base_endpoint)

    def test_allows_a_single_image_to_be_processed(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        response = api.find_object([
            {'url': 'https://www.placecage.com/c/200/300'},
        ], [
            {'class': 'person'},
        ])
        assert len(response['imageResults']) == 1
        assert len(response['jobResults']) == 0
        assert response['status'] == 'IN_PROGRESS'

    def test_does_not_allow_very_long_image_urls(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)

        image_url = 'http://example.com/' + gen_random_string(1024) + '.jpg'
        with pytest.raises(ApiRequestError):
            api.find_object([{'url': image_url}], [{'class': 'person'}])

    def test_allows_multiple_images_to_be_processed(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        response = api.find_object([
            {'url': 'https://www.placecage.com/c/200/300'},
            {'url': 'https://www.placecage.com/c/200/300'},
            {'url': 'https://www.placecage.com/c/200/300'},
        ], [
            {'class': 'person'},
        ])
        assert len(response['imageResults']) == 3
        assert len(response['jobResults']) == 0
        assert response['status'] == 'IN_PROGRESS'

    def test_does_not_allow_empty_images(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        with pytest.raises(ApiRequestError):
            api.find_object([], [{'class': 'person'}])

    def test_does_not_allow_more_than_64_images(self):
        max_image_batch_size = 64

        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        images = [
            {'url': 'https://www.placecage.com/c/200/300'} for _ in range(max_image_batch_size + 1)
        ]
        assert len(images) > max_image_batch_size
        with pytest.raises(ApiRequestError):
            api.find_object(images, [{'class': 'person'}])

    def test_images_should_all_have_valid_urls(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        with pytest.raises(ApiRequestError):
            api.find_object([{'url': 'xxx'}], [{'class': 'person'}])

    def test_allows_multiple_classes_to_be_specified(self):
        # api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        # response = api.find_object([
        #     {'url': 'https://www.placecage.com/c/200/300'},
        # ], [
        #     {'class': 'car'}, {'class': 'person'},
        # ])
        # assert response['status'] == 'IN_PROGRESS'
        pass
        # TODO: Handle this properly.

    def test_does_not_allow_unaccepted_classes(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        with pytest.raises(ApiRequestError):
            api.find_object([
                {'url': 'https://www.placecage.com/c/200/300'},
            ], [{'class': 'dancing-pig'}])

    def test_class_hitl_must_be_valid(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        with pytest.raises(ApiRequestError):
            api.find_object([
                {'url': 'https://www.placecage.com/c/200/300'},
            ], [
                {'class': 'person', 'hitl': 'XXX'},
            ])

    def test_allow_multiple_classes_with_different_hitl(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        response = api.find_object([
            {'url': 'https://www.placecage.com/c/200/300'},
        ], [
            {'class': 'person', 'hitl': 'ALWAYS'},
            {'class': 'person', 'hitl': 'NEVER'},
        ])
        # TODO: Handle this properly.

    def test_does_not_allow_empty_classes(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        with pytest.raises(ApiRequestError):
            api.find_object([
                {'url': 'https://www.placecage.com/c/200/300'},
            ], [])

    def test_webhook_url_must_be_a_valid_url(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        with pytest.raises(ApiRequestError):
            api.find_object([{'url': 'https://xxx'}], [{'class': 'person', 'hitl': 'NEVER'}], webhook_url='xxx')

    def test_does_not_allow_large_custom_or_feed_ids(self):
        api = ImageIntelligenceApi(self.client_id, self.client_secret, self.base_endpoint, self.token)
        images = [{'url': 'https://www.placecage.com/c/200/300'}]
        classes = [{'class': 'person', 'hitl': 'NEVER'}]

        with pytest.raises(ApiRequestError):
            api.find_object(images, classes, feed_id=gen_random_string(1024))
        with pytest.raises(ApiRequestError):
            api.find_object(images, classes, custom_id=gen_random_string(1024))
