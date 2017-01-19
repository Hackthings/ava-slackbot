# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
from slackbot.bot import Bot
from slackbot import settings

def main():

    settings.API_TOKEN = ""
    settings.DEFAULT_REPLY = "Sorry but I didn't understand you"
    settings.PLUGINS = [
        'bot'
    ]

    logging.basicConfig()

    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()