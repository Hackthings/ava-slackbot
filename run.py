#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json

from functools import partial

from avabot.config import load as load_config
from avabot.vendor.slack import Slack
from avabot.services.parsers import MessageParser

from avabot.commands.detect import Detect
from avabot.commands.consensus import Consensus
from avabot.vendor.ava import AvaApi
from avabot.domain import AvaSlackbotException
from avabot.services.validators import docopt_arg_validator


def send_error_message(slack_client, error_message, arguments):
    slack_client.send_formatted_message(
        'An error has occurred processing your request...',
        error_message,
        arguments['channel'],
        arguments['user']
    )


def handle_message(slack_client, ava_client, config, arguments):
    try:
        args = docopt_arg_validator(arguments)
        if '--extras' in args:
            slack_client.send_formatted_message(
                'See `--help` usage or `--version` below:',
                args['--extras'],
                args['channel'],
                args['user']
            )
        elif any([args['detect'], args['d']]):
            Detect(config, ava_client, slack_client, **args)
        elif any([args['consensus'], args['c']]):
            Consensus(config, ava_client, slack_client, **args)
        elif any([args['find-person'], args['fp']]):
            slack_client.send_message('`find-person` not yet implemented :cry:', args['channel'])
        elif any([args['search'], args['s']]):
            slack_client.send_message('`search` not yet implemented :cry:', args['channel'])
        else:
            logging.error('unexpected args %s' % args)
    except AvaSlackbotException as e:
        if isinstance(e.message, dict):
            error_message = json.dumps(e.message, indent=2, sort_keys=True)
        else:
            error_message = str(e)

        send_error_message(slack_client, error_message, arguments)
    except ValueError as e:
        send_error_message(slack_client, str(e), arguments)


def main():
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    ava_client = AvaApi(
        config.ava.client_id,
        config.ava.client_secret,
        config.ava.endpoint,
        config.ava.version
    )

    slack_client = Slack(config.slack, MessageParser())
    slack_client.listen(partial(handle_message, slack_client, ava_client, config))


if __name__ == '__main__':
    main()
