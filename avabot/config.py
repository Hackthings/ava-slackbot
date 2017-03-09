# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

__all__ = ['config']

config = None


class Config(object):
    __shared_state = {}

    def __init__(self, path):
        self.__dict__ = self.__shared_state

        self.config_path = path or self.config_path
        self._config = {}

    def load(self):
        load_dotenv(self.config_path)
        self._config['MIN_CONFIDENCE'] = float(os.environ['MIN_CONFIDENCE'])
        self._config['WHITELIST_CHANNELS'] = os.environ['WHITELIST_CHANNELS'].split(',')

        self._config['AVA_API_ENDPOINT'] = os.environ['AVA_API_ENDPOINT']
        self._config['AVA_API_VERSION'] = os.environ['AVA_API_VERSION']
        self._config['AVA_CLIENT_ID'] = os.environ['AVA_CLIENT_ID']
        self._config['AVA_CLIENT_SECRET'] = os.environ['AVA_CLIENT_SECRET']

        self._config['SLACK_API_TOKEN'] = os.environ['SLACK_API_TOKEN']
        self._config['MIN_CONFIDENCE'] = float(os.environ['MIN_CONFIDENCE'])
        self._config['AWS_ACCESS_KEY_ID'] = os.environ['AWS_ACCESS_KEY_ID']
        self._config['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
        self._config['S3_RESULTS_BUCKET'] = os.environ['S3_RESULTS_BUCKET']
        self._config['WHITELIST_CHANNELS'] = os.environ['WHITELIST_CHANNELS'].split(',')

    def get(self, key):
        return self._config[key]
