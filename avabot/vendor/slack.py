# -*- coding: utf-8 -*-
from slackbot.bot import settings


def should_respond_to_message(message, whitelist=settings.WHITELIST_CHANNELS):
    return message.body['channel'] in whitelist
