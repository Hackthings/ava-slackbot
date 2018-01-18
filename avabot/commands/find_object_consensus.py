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
        results_message = [
            '<@%s> OK `/find-object/{id}`:\n' % self.kwargs['user'],
        ]
        target_image = results[0]['imageResults'][0]['url']
        for i, result in enumerate(results):
            image_results = result['imageResults'][0]

            for obj in image_results['objects']:
                results_message.append('*modelId:* %s, `%s:%s`' % (self.MODEL_IDS[i], obj['class'], obj['confidence']))

        results_message.append('\n*Target image:* %s' % target_image)
        return '\n'.join(results_message)

    def call_api_with_model_id(self, model_id):
        image_urls = self.kwargs['<urls>']

        # get class from args
        # todo: factor out and reuse
        classes = set()
        if self.kwargs.get('--class'):
            classes.add(self.kwargs.get('--class'))

        if self.kwargs.get('-c'):
            classes.add("car")

        if self.kwargs.get('-p'):
            classes.add("person")

        if len(classes) == 0:
            classes = {DEFAULT_CLASS}

        logging.info('posting to /v2/find-object - urls=%s' % image_urls)
        try:
            response = self.ii_client.find_object(
                [{'url': image} for image in image_urls],
                [{'class': class_, 'hitl': 'NEVER', 'model': model_id} for class_ in classes],
                custom_id='ava-slackbot-' + str(uuid.uuid4()),
            )
        except ApiRequestError as e:
            logging.info('failed to POST /v2/find-object - urls=%s, error=%s' % (image_urls, e))
            return

        success_message = 'successfully POST\'d to /v2/find-object, polling for results -url=${url} - jobId={job_id}'
        logging.info(success_message.format(**{
            'url': image_urls,
            'job_id': response['id'],
        }))
        return self.ii_client.poll_for_object_result(response['id'])

    def run(self):
        is_raw_json = self.kwargs['--raw-json']

        results = []
        for model_id in self.MODEL_IDS:
            print(model_id)
            results.append(self.call_api_with_model_id(model_id))

        if is_raw_json:
            self.slack_client.send_formatted_message(
                'OK `/find-object/{id}` - JSON:',
                json.dumps(results, indent=2, sort_keys=True),
                self.kwargs['channel'],
                self.kwargs['user']
            )
        else:
            self.slack_client.send_formatted_message(
                None,
                self.parse_results(results),
                self.kwargs['channel'],
                self.kwargs['user'],
                is_code=False,
            )
