# -*- coding: utf-8 -*-
from slackbot.bot import settings

config = settings.config
DEFAULT_WHITELIST_CHANNELS = config.get('WHITELIST_CHANNELS')


def should_respond_to_message(message, whitelist=DEFAULT_WHITELIST_CHANNELS):
    return message.body['channel'] in whitelist
