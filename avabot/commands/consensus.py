# -*- coding: utf-8 -*-
import json
from http import HTTPStatus

from avabot.commands import Command
from avabot.domain.exceptions.command import DetectionError


class Consensus(Command):
    def __init__(self, config, ava_client, slack_client, **kwargs):
        self.ava_client = ava_client
        self.slack_client = slack_client

        self.model_list = [
            'DETECTOR_GEN_01',
            'CLASSIFIER_GEN_01',
            'CLASSIFIER_IR_01',
        ]

        super().__init__(config, **kwargs)

    def _parse_detection_results(self, responses):
        detection_results = [
            '<@%s> Consensus detections:\n' % (
                self.kwargs['user']
            )
        ]

        for response in responses:
            detection = response['body']
            result = detection['results'][0]  # always 1

            objects = sorted(result['objects'], key=lambda k: k['confidence'], reverse=True)
            objects = objects[:self.kwargs.get('--head')]

            if self.kwargs['--all']:
                detection_results.append('\t• *model:* %s, *status*: %s' % (
                    detection['model'],
                    detection['status']['code']
                ))
                for obj in objects:
                    detection_result = '\t\t◦ `%s`: %s' % (
                        obj['class'],
                        obj['confidence']
                    )
                    detection_results.append(detection_result)
            else:
                for obj in objects:
                    if obj['class'] == 'person':
                        detection_result = '\t• *model:* %s: `%s`, %s (*status*: %s)' % (
                            detection['model'],
                            obj['class'],
                            obj['confidence'],
                            detection['status']['code']
                        )
                        detection_results.append(detection_result)
                        break

            if len(objects) == 0:
                if self.kwargs['--all']:
                    detection_results.append('\t\t◦ no objects found')
                else:
                    detection_results.append('\t• *model:* %s: no objects found' % detection['model'])

        detection_results.append('\n*Target image*: %s' % self.kwargs['<url>'])
        return '\n'.join(detection_results)

    def run(self):
        responses = []
        for model in self.model_list:
            response = self.ava_client.detect(
                self.kwargs['<url>'],
                model=model
            )
            if response['code'] != HTTPStatus.OK:
                raise DetectionError(response['body'])
            responses.append(response)

        poll_responses = []
        for response in responses:
            poll_response = self.ava_client.poll_until_complete(response['body']['id'])
            if poll_response['code'] != HTTPStatus.OK:
                raise DetectionError(poll_response['body'])
            poll_responses.append(poll_response)

        if self.kwargs['--raw-json']:
            for poll_response in poll_responses:
                self.slack_client.send_formatted_message(
                    'Successfully processed detection. Raw JSON response:',
                    json.dumps(poll_response['body'], indent=2, sort_keys=True),
                    self.kwargs['channel'],
                    self.kwargs['user']
                )
        else:
            detection_results = self._parse_detection_results(poll_responses)
            self.slack_client.send_message(detection_results, self.kwargs['channel'])
