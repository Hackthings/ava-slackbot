# -*- coding: utf-8 -*-
import uuid
import logging
import json

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError
from avabot.constants import DEFAULT_CLASS


class FindObjectConsensus(Command):
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
        results_message = [f'<@{user}> OK `/find-object/`:\n']
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

        # get classes from args
        classes = set(self.kwargs['--class'])

        if self.kwargs['-c']:
            classes.add('car')

        if self.kwargs['-p']:
            classes.add('person')

        if len(classes) == 0:
            classes = {DEFAULT_CLASS}

        logging.info(f'posting to /v2/find-object - urls={image_urls}')

        images = [{'url': image} for image in image_urls]
        classes = [{'class': cls, 'hitl': 'NEVER', 'model': model_id} for cls in classes]

        try:
            response = self.ii_client.find_object(images, classes, custom_id='ava-slackbot-' + str(uuid.uuid4()))
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/find-object - urls={image_urls}, error={e}')
            return

        job_id = response['id']
        logging.info(f'successfully POST\'d to /v2/find-object, polling results -url=${image_urls} - jobId={job_id}')
        return self.ii_client.poll_for_object_result(response['id'])

    def run(self):
        is_raw_json = self.kwargs['--raw-json']

        results = []
        for model_id in self.MODEL_IDS:
            results.append(self.call_api_with_model_id(model_id))

        if is_raw_json:
            self.slack_client.send_formatted_message('OK `/find-object/` - JSON:',
                                                     json.dumps(results, indent=2, sort_keys=True),
                                                     self.kwargs['channel'], self.kwargs['user'])
        else:
            self.slack_client.send_formatted_message(
                None, self.parse_results(results), self.kwargs['channel'], self.kwargs['user'], is_code=False)
