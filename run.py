#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from avabot import config as app_config
from avabot.vendor.slack import Slack
from avabot.services.parsers import MessageParser


def handle_message(arguments) -> None:
    logging.info(arguments)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('init ava-slackbot!')

    config = app_config.load()

    slack = Slack(config.slack, MessageParser())
    slack.listen(handle_message)

if __name__ == '__main__':
    main()
