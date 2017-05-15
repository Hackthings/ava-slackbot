# -*- coding: utf-8 -*-
import logging
import time

from typing import List, Dict, Optional, Callable

from slackclient import SlackClient
from ..config import SlackConfig
from ..services.parsers import MessageParser

from ..domain.parse_exceptions import AvaSlackbotException

ParsedSlackMessage = Optional[Dict]
MessageHandler = Callable[[Dict], None]


class Slack:
    def __init__(self, config: SlackConfig, message_parser: MessageParser) -> None:
        self.config = config
        self.client = SlackClient(config.api_token)
        self.message_parser = message_parser

    def _should_respond(self, message: Dict):
        user = message.get('user')
        type_ = message.get('type')
        text = message.get('text')

        if not message:
            return False
        if not text:
            return False
        if not type_ or type_ != 'message':
            return False
        if not user or user == self.config.bot_id:
            return False
        return True

    def _format_invalid_message(self, message: Dict, error_message: str) -> str:
        return '\n'.join([
            '<@%s> Bad command, RTFM! `@%s --help` for more details. See usage below:' % (
                message['user'],
                self.config.bot_name,
            ),
            '```',
            error_message,
            '```',
        ])

    def _parse_message(self, message: Dict) -> Optional[ParsedSlackMessage]:
        if not self._should_respond(message):
            return None

        text = message['text']
        channel = message['channel']
        user = message['user']
        logging.info('received acceptable message "%s" from user "%s"' % (text, user))

        try:
            return self.message_parser.run(text, channel, user)
        except AvaSlackbotException as e:
            logging.info('"%s" deemed an invalid message by our message_parser' % text)
            response = self._format_invalid_message(message, str(e))
            self.client.api_call('chat.postMessage', channel=channel, text=response, as_user=True, link_names=True)
            return None

    def _process_messages(self, messages: List[Dict], handler: MessageHandler) -> None:
        processed_messages = map(self._parse_message, messages)
        processed_messages = filter(None.__ne__, processed_messages)
        processed_messages = map(handler, processed_messages)
        list(processed_messages)

    def listen(self, handler: MessageHandler) -> None:
        if self.client.rtm_connect():
            logging.info('connected to slack, ready to accept messages')
            while True:
                slack_messages = self.client.rtm_read()
                self._process_messages(slack_messages, handler)
                time.sleep(self.config.websocket_delay)
        else:
            logging.error('failed to connect to slack, perhaps invalid token')
            raise RuntimeError()
