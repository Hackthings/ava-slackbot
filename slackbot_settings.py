# -*- coding: utf-8 -*-
import os

API_TOKEN = os.environ.get('AVA_BOT_SLACK_API_TOKEN')
DEFAULT_REPLY = "Sorry but I didn't understand you"

PLUGINS = [
    'avabot.plugins',
]
