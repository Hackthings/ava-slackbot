# -*- coding: utf-8 -*-
import uuid
import logging

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

    def request(self):
        image_urls = self.kwargs['<urls>']
        targets = self.kwargs['--target']

        logging.info(f'posting to /v2/find-target - urls={image_urls}')
        images = [{'url': image} for image in image_urls]
        target = {'class': 'person', 'images': [t.strip('<>') for t in targets]}
        try:
            return self.ii_client.find_target(images, target, custom_id='ava-slackbot-' + str(uuid.uuid4()))
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/find-target - urls={image_urls}, error={e}')
            return
