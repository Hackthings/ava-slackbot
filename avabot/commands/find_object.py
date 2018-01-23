# -*- coding: utf-8 -*-
import uuid
import logging
import json

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError
from avabot.constants import DEFAULT_CLASS, DEFAULT_HITL


class FindObject(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        user = self.kwargs['user']
        job_id = results['id']
        status = results['status']
        results_message = [f'<@{user}> OK `/find-object/{job_id}` *{status}*:\n']

        for image_result in results['imageResults']:
            img_result_url = image_result['url']
            results_message.append(f'\n*Target image:* {img_result_url}\n')
            for obj in image_result['objects']:
                cls = obj['class']
                cnf = obj['confidence']
                results_message.append(f'`{cls}:{cnf}`')
        return '\n'.join(results_message)

    def run(self):
        image_urls = self.kwargs['<urls>']
        classes = self.kwargs['--class'] or [DEFAULT_CLASS]
        model_id = self.kwargs['--model']
        hitl = self.kwargs.get('--hitl') or DEFAULT_HITL
        is_raw_json = self.kwargs['--raw-json']

        logging.info(f'posting to /v2/find-object - url={image_urls}')

        images = [{'url': image} for image in image_urls]
        classes = [{'class': cls, 'hitl': hitl, 'model': model_id} for cls in classes]

        try:
            response = self.ii_client.find_object(images, classes, custom_id='ava-slackbot-' + str(uuid.uuid4()))
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/find-object - urls={image_urls}, error={e}')
            return

        job_id = response['id']
        logging.info(f'successfully POST\'d to /v2/find-object, polling results -urls=${image_urls} - jobId={job_id}')

        result = self.ii_client.poll_for_object_result(response['id'])
        if is_raw_json:
            self.slack_client.send_formatted_message(f'OK `/find-object/{job_id}` - JSON:',
                                                     json.dumps(result, indent=2, sort_keys=True),
                                                     self.kwargs['channel'], self.kwargs['user'])
        else:
            self.slack_client.send_formatted_message(
                None, self.parse_results(result), self.kwargs['channel'], self.kwargs['user'], is_code=False)
