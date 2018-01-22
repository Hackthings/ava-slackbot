# -*- coding: utf-8 -*-
import uuid
import logging
import json

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError


class FindTarget(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        results_message = [
            '<@%s> OK -- submitted `/find-target` job %s\n' %
            (self.kwargs['user'], results['id']),
        ]
        return '\n'.join(results_message)

    def run(self):
        image_urls = self.kwargs['<urls>']
        target = self.kwargs['--target'][1:]
        is_raw_json = self.kwargs['--raw-json']

        logging.info('posting to /v2/find-target - urls=%s' % image_urls)
        try:
            response = self.ii_client.find_target(
                [{
                    'url': image
                } for image in image_urls],
                {'class': "person",
                 'images': [target]},
                custom_id='ava-slackbot-' + str(uuid.uuid4()),
            )
        except ApiRequestError as e:
            logging.info('failed to POST /v2/find-target - urls=%s, error=%s' %
                         (image_urls, e))
            return

        if is_raw_json:
            self.slack_client.send_formatted_message(
                'OK `/find-target/%s` - JSON:' % response['id'],
                json.dumps(response, indent=2, sort_keys=True),
                self.kwargs['channel'], self.kwargs['user'])
        else:
            self.slack_client.send_formatted_message(
                None,
                self.parse_results(response),
                self.kwargs['channel'],
                self.kwargs['user'],
                is_code=False,
            )
