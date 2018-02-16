# -*- coding: utf-8 -*-
import uuid
import logging

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError
from avabot.constants import DEFAULT_CLASS


class DetectConsensus(Command):
    MODEL_IDS = [
        '817453cc-3ead-46df-8db2-dff517c01fba',
        '2bc4b9ae-9f16-4a94-99eb-39473377dc5f',
    ]

    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        user = self.kwargs['user']
        results_message = [f'<@{user}> OK `/detect/`:\n']
        target_image = results[0]['imageResults'][0]['url']

        for i, result in enumerate(results):
            image_results = result['imageResults'][0]

            for obj in image_results['objects']:
                cls = obj['class']
                cnf = obj['confidence']
                model_id = self.MODEL_IDS[i]
                results_message.append(f'*modelId:* {model_id}, `{cls}:{cnf}`')

        results_message.append(f'\n*Target image:* {target_image}')
        return '\n'.join(results_message)

    def call_api_with_model_id(self, model_id):
        image_urls = self.kwargs['<urls>']
        classes = self.kwargs['--class'] or [DEFAULT_CLASS]

        logging.info(f'posting to /v2/detect - urls={image_urls}')

        images = [{'url': image} for image in image_urls]
        classes = [{'class': cls, 'hitl': 'NEVER', 'model': model_id} for cls in classes]

        try:
            response = self.ii_client.detect(images, classes, custom_id='ava-slackbot-' + str(uuid.uuid4()))
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/detect - urls={image_urls}, error={e}')
            return

        job_id = response['id']
        logging.info(f'successfully POST\'d to /v2/detect, polling results -url=${image_urls} - jobId={job_id}')
        return self.ii_client.poll_for_detect_result(response['id'])

    def request(self):
        results = []
        for model_id in self.MODEL_IDS:
            results.append(self.call_api_with_model_id(model_id))
        return results
