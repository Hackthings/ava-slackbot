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
        image_results = results['imageResults'][0]
        results_message = [
            '<@%s> OK `/find-object/%s` *%s*:\n' % (
                self.kwargs['user'], results['id'], results['status'],
            ),
        ]

        for obj in image_results['objects']:
            results_message.append('`%s:%s`' % (obj['class'], obj['confidence']))
        results_message.append('\n*Target image:* %s' % image_results['url'])
        return '\n'.join(results_message)

    def run(self):
        image_url = self.kwargs['<url>']
        class_ = self.kwargs.get('<class>') or DEFAULT_CLASS
        model_id = self.kwargs['<model_id>']
        hitl = self.kwargs.get('--hitl') or DEFAULT_HITL
        is_raw_json = self.kwargs['--raw-json']

        logging.info('posting to /v2/find-object - url=%s' % image_url)
        try:
            response = self.ii_client.find_object(
                [{'url': image_url}],
                [{'class': class_, 'hitl': hitl, 'model': model_id}],
                custom_id='ava-slackbot-' + str(uuid.uuid4()),
            )
        except ApiRequestError as e:
            logging.info('failed to POST /v2/find-object - url=%s, error=%s' % (image_url, e))
            return

        success_message = 'successfully POST\'d to /v2/find-object, polling for results -url=${url} - jobId={job_id}'
        logging.info(success_message.format(**{
            'url': image_url,
            'job_id': response['id'],
        }))

        result = self.ii_client.poll_for_object_result(response['id'])
        if is_raw_json:
            self.slack_client.send_formatted_message(
                'OK `/find-object/%s` - JSON:' % result['id'],
                json.dumps(result, indent=2, sort_keys=True),
                self.kwargs['channel'],
                self.kwargs['user']
            )
        else:
            self.slack_client.send_formatted_message(
                None,
                self.parse_results(result),
                self.kwargs['channel'],
                self.kwargs['user'],
                is_code=False,
            )