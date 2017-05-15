#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging


def main():
    logging.basicConfig(level=logging.INFO)

    logging.info('init ava-slackbot!')

    # config = Config(os.path.join(os.path.dirname(__file__), '.env'))
    # config.load()
    #
    # ava_client = AvaAPI(
    #     config.get('AVA_CLIENT_ID'),
    #     config.get('AVA_CLIENT_SECRET'),
    #     config.get('AVA_API_ENDPOINT'),
    #     config.get('AVA_API_VERSION')
    # )
    #
    # settings.PLUGINS = [
    #     'avabot.plugins',
    # ]
    # settings.API_TOKEN = config.get('SLACK_API_TOKEN')
    # settings.config = config
    # settings.ava_client = ava_client
    #
    # bot = Bot()
    # logging.info('ava-slackbot running. ready to accept messages')
    # bot.run()

if __name__ == '__main__':
    main()
