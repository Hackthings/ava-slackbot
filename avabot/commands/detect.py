# -*- coding: utf-8 -*-
import json

from http import HTTPStatus
from typing import Dict

from . import Command
from ..config import Config
from ..vendor.ava import AvaApi
from ..vendor.slack import Slack
from ..domain.exceptions.command import DetectionError


class Detect(Command):
    def __init__(self, config: Config, ava_client: AvaApi, slack_client: Slack, **kwargs) -> None:
        self.ava_client = ava_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def _parse_detection_results(self, response: Dict) -> str:
        detection = response['body']
        detection_results = [
            '<@%s> Detection: *%s*:\n' % (
                self.kwargs['user'], detection['status']['code']
            )
        ]

        result = detection['results'][0]  # always 1
        objects = sorted(result['objects'], key=lambda k: k['confidence'], reverse=True)
        objects = objects[:self.kwargs.get('--head')]

        for obj in objects:
            detection_result = '\t• `%s`: %s (*model:* %s)' % (
                obj['class'],
                obj['confidence'],
                detection['model']
            )
            detection_results.append(detection_result)
        if len(result['objects']) == 0:
            detection_results.append('_No objects were found in the target image..._')
        detection_results.append('\n*Target image*: %s' % result['url'])
        return '\n'.join(detection_results)

    def run(self) -> None:
        response = self.ava_client.detect(
            self.kwargs['<url>'],
            model=self.kwargs['--model'],
            version=self.kwargs['--mversion'],
        )
        if response['code'] != HTTPStatus.OK:
            raise DetectionError(response['body'])

        poll_response = self.ava_client.poll_until_complete(response['body']['id'])
        if poll_response['code'] != HTTPStatus.OK:
            raise DetectionError(poll_response['body'])

        if self.kwargs['--raw-json']:
            self.slack_client.send_formatted_message(
                'Successfully processed detection. Raw JSON response:',
                json.dumps(poll_response['body'], indent=2, sort_keys=True),
                self.kwargs['channel'],
                self.kwargs['user']
            )
        else:
            detection_results = self._parse_detection_results(poll_response)
            self.slack_client.send_message(detection_results, self.kwargs['channel'])
