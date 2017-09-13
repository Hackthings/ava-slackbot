# -*- coding: utf-8 -*-
import logging
import time
from typing import List, Dict, Optional, Callable

from slackclient import SlackClient

from ..config import SlackConfig
from ..services.parsers import MessageParser
from ..domain.exceptions.parse import AvaSlackbotException

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

        # No 'text' in the event means it's an event we don't care about.
        if not text:
            return False

        # Double check the target user is `@our-slackbot`.
        if not text.strip().startswith('<@%s>' % self.config.bot_id):
            return False

        # Make sure the message type is a 'message' so we don't blow up downstream.
        if not type_ or type_ != 'message':
            return False

        # Don't reply to ourselves because Ava isn't a crazy bot.
        if not user or user == self.config.bot_id:
            return False

        return True

    def _parse_message(self, message: Dict) -> Optional[ParsedSlackMessage]:
        text = message.get('text')
        channel = message.get('channel')
        user = message.get('user')

        if not self._should_respond(message):
            logging.info('denied message "%s" from user "%s' % (text, user))
            return None

        logging.info('received acceptable message "%s" from user "%s"' % (text, user))

        try:
            return self.message_parser.run(text, channel, user)
        except AvaSlackbotException as e:
            logging.info('"%s" deemed an invalid message by our message_parser' % text)
            self.send_formatted_message(
                'Bad command! `@%s --help` for details. See usage below:' % self.config.bot_name,
                str(e),
                channel,
                user
            )

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

    def send_message(self, message: str, channel: str) -> None:
        self.client.api_call(
            'chat.postMessage',
            channel=channel,
            text=message,
            as_user=True,
            link_names=True
        )

    def send_formatted_message(
        self,
        header: str,
        message: str,
        channel: str,
        user: str,
        is_code: bool = True
    ) -> None:
        formatted_message = [
            '<@%s> %s' % (user, header),
            '```' if is_code else None,
            message,
            '```' if is_code else None,
        ]
        formatted_message = list(filter(None.__ne__, formatted_message))
        formatted_message = '\n'.join(formatted_message)

        self.send_message(formatted_message, channel)
