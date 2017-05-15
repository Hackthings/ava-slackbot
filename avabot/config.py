# -*- coding: utf-8 -*-
import os
from typing import Dict


class AvaApiConfig:
    def __init__(self, endpoint: str, version: str, client_id: str, client_secret: str) -> None:
        self.endpoint = endpoint
        self.version = version
        self.client_id = client_id
        self.client_secret = client_secret


class SlackConfig:
    def __init__(self, bot_id: str, bot_name: str, api_token: str, whitelist_channels: str, websocket_delay: int) -> None:
        self.bot_id = bot_id
        self.bot_name = bot_name
        self.api_token = api_token
        self.whitelist_channels = whitelist_channels
        self.websocket_delay = websocket_delay


class Config:
    def __init__(self, ava: AvaApiConfig, slack: SlackConfig) -> None:
        self.ava = ava
        self.slack = slack


def _load_unsafe() -> Dict:
    return {
        'AVA_API_ENDPOINT': os.environ['AVA_API_ENDPOINT'],
        'AVA_API_VERSION': os.environ['AVA_API_VERSION'],
        'AVA_CLIENT_ID': os.environ['AVA_CLIENT_ID'],
        'AVA_CLIENT_SECRET': os.environ['AVA_CLIENT_SECRET'],

        'SLACK_API_TOKEN': os.environ['SLACK_API_TOKEN'],
        'SLACK_WHITELIST_CHANNELS': os.environ['SLACK_WHITELIST_CHANNELS'],
        'SLACK_WEBSOCKET_DELAY': int(os.environ.get('SLACK_WEBSOCKET_DELAY', 1)),
        'SLACK_BOT_ID': os.environ['SLACK_BOT_ID'],
        'SLACK_BOT_NAME': os.environ.get('SLACK_BOT_NAME', 'ava'),
    }


def load() -> Config:
    env = _load_unsafe()
    return Config(
        AvaApiConfig(
            env['AVA_API_ENDPOINT'],
            env['AVA_API_VERSION'],
            env['AVA_CLIENT_ID'],
            env['AVA_CLIENT_SECRET']
        ),
        SlackConfig(
            env['SLACK_BOT_ID'],
            env['SLACK_BOT_NAME'],
            env['SLACK_API_TOKEN'],
            env['SLACK_WHITELIST_CHANNELS'],
            env['SLACK_WEBSOCKET_DELAY']
        )
    )
