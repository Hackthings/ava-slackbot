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
        user = self.kwargs['user']
        job_id = results['id']
        return f'<@{user}> OK -- submitted `/find-target` job id `{job_id}`\n'

    def run(self):
        image_urls = self.kwargs['<urls>']
        target = self.kwargs['--target'][1:]
        is_raw_json = self.kwargs['--raw-json']

        logging.info(f'posting to /v2/find-target - urls={image_urls}')
        images = [{'url': image} for image in image_urls]
        target = {'class': "person", 'images': [target]}
        try:
            response = self.ii_client.find_target(images, target, custom_id='ava-slackbot-' + str(uuid.uuid4()))
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/find-target - urls={image_urls}, error={e}')
            return

        job_id = response['id']
        if is_raw_json:
            self.slack_client.send_formatted_message(f'OK `/find-target/{job_id}` - JSON:',
                                                     json.dumps(response, indent=2, sort_keys=True),
                                                     self.kwargs['channel'], self.kwargs['user'])
        else:
            self.slack_client.send_formatted_message(
                None, self.parse_results(response), self.kwargs['channel'], self.kwargs['user'], is_code=False)
