# -*- coding: utf-8 -*-
import uuid
import logging

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError
from avabot.constants import DEFAULT_CLASS, DEFAULT_HITL


class Detect(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        user = self.kwargs['user']
        job_id = results['id']
        status = results['status']
        results_message = [f'<@{user}> OK `/detect/{job_id}` *{status}*:\n']

        for image_result in results['imageResults']:
            img_result_url = image_result['url']
            results_message.append(f'\n*Target image:* {img_result_url}\n')
            for obj in image_result['objects']:
                cls = obj['class']
                cnf = obj['confidence']
                results_message.append(f'`{cls}:{cnf}`')
        return '\n'.join(results_message)

    def request(self):
        image_urls = self.kwargs['<urls>']
        classes = self.kwargs['--class'] or [DEFAULT_CLASS]
        model_id = self.kwargs['--model']
        verify = self.kwargs.get('--verify') or DEFAULT_HITL

        images = [{'url': image} for image in image_urls]
        classes = [{'class': cls, 'verify': verify, 'model': model_id} for cls in classes]

        logging.info(f'posting to /v2/detect - url={image_urls}')

        try:
            response = self.ii_client.detect(images, classes, custom_id='ava-slackbot-' + str(uuid.uuid4()))
            result = self.ii_client.poll_for_detect_result(response['id'])
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/detect - urls={image_urls}, error={e}')
            raise e

        logging.info(f'successfully POST\'d to /v2/detect')
        return result
