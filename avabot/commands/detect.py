# -*- coding: utf-8 -*-
import json

from avabot.domain.exceptions.command import DetectionError
from . import Command
from ..config import Config
from ..vendor.ava import AvaApi
from ..vendor.slack import Slack


class Detect(Command):
    def __init__(self, config: Config, ava_client: AvaApi, slack_client: Slack, **kwargs) -> None:
        self.ava_client = ava_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def run(self) -> None:
        response = self.ava_client.detect(
            self.kwargs['<url>'],
            model=self.kwargs['--model']
        )
        if response['code'] != 200:
            raise DetectionError(response['body'])

        poll_response = self.ava_client.poll_until_complete(response['body']['id'])
        if poll_response['code'] != 200:
            raise DetectionError(poll_response['body'])

        if self.kwargs['--raw-json']:
            self.slack_client.send_formatted_message(
                'Successfully processed detection. Raw JSON response:',
                json.dumps(poll_response['body'], indent=2, sort_keys=True),
                self.kwargs['channel'],
                self.kwargs['user']
            )
        else:
            detection_results = [
                '<@%s> Successfully processed detection (*tip:* `--raw-json`):\n' % self.kwargs['user']
            ]
            result = poll_response['body']['results'][0]
            for detection in result['objects']:  # always 1
                detection_result = '\t• `%s`: %s (*model:* %s)' % (
                    detection['class'],
                    detection['confidence'],
                    poll_response['body']['model']
                )
                detection_results.append(detection_result)
            detection_results.append('\n*Target image*: %s' % result['url'])
            detection_results = '\n'.join(detection_results)
            self.slack_client.send_message(detection_results, self.kwargs['channel'])
