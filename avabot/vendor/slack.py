# -*- coding: utf-8 -*-
import logging
import time

from slackclient import SlackClient

from avabot.exceptions.parse import AvaSlackbotException


class Slack:
    def __init__(self, config, message_parser):
        self.config = config
        self.client = SlackClient(config.api_token)
        self.message_parser = message_parser

    def _should_respond(self, type_, text, channel, user):
        """Determines whether or not the Slackbot should process and reply to the message."""
        # Only allow messages to pass through if the channel is whitelisted.
        if channel not in self.config.whitelist_channels:
            return False

        # No 'text' in the event means it's an event we don't care about.
        if not text:
            return False

        # Double check the target user is `@our-slackbot`.
        if not text.strip().startswith('<@%s>' % self.config.bot_id):
            return False

        # Make sure the message type is a 'message' so we don't blow up downstream.
        if type_ != 'message':
            return False

        # Slack-bot shouldn't reply to itself.
        if user == self.config.bot_id:
            return False

        return True

    def _parse_message(self, message):
        user = message.get('user')
        type_ = message.get('type')
        text = message.get('text')
        channel = message.get('channel')

        if not self._should_respond(type_, text, channel, user):
            logging.debug('denied message from user - message=%s - user=%s' % (text, user))
            return None

        # replace slack's unicode quotes with the normal ones so it can be parsed correcty
        text = str(text).replace(u'\u201c', '"').replace(u'\u201d', '"')

        logging.info('received acceptable message from user - message=%s - user=%s' % (text, user))
        try:
            return self.message_parser.run(text, channel, user)
        except AvaSlackbotException as e:
            logging.info('"%s" is an invalid message to process' % text)
            self.send_formatted_message(
                'Bad command! `@%s --help` for details. See usage below:' % self.config.bot_name,
                str(e),
                channel,
                user
            )
        return None

    def listen(self, handler):
        """Starts listening for user input via `self.client`."""
        if self.client.rtm_connect():
            logging.info('connected to slack, ready to accept messages')
            while True:
                processed_messages = map(self._parse_message, self.client.rtm_read())
                processed_messages = filter(None.__ne__, processed_messages)
                processed_messages = map(handler, processed_messages)
                list(processed_messages)
                time.sleep(self.config.websocket_delay)
        else:
            logging.error('failed to connect to slack, perhaps invalid token')
            raise RuntimeError()

    def send_message(self, message, channel):
        self.client.api_call('chat.postMessage', channel=channel, text=message, as_user=True, link_names=True)

    def send_formatted_message(self, header, message, channel, user, is_code=True):
        formatted_message = [
            '<@%s> %s' % (user, header) if header else None,
            '```' if is_code else None,
            message,
            '```' if is_code else None,
        ]
        formatted_message = list(filter(None.__ne__, formatted_message))
        formatted_message = '\n'.join(formatted_message)

        self.send_message(formatted_message, channel)
