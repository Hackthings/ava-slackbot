# -*- coding: utf-8 -*-
import logging
import json

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError


class GetFindObject(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        message = [
            '<@%s> OK `/find-object/%s`' % (self.kwargs['user'],
                                            results['id']),
        ]
        message.append('\n*Job Status:* %s\n' % results['status'])

        if results['status'] == "COMPLETED_SUCCESSFULLY":
            for image_result in results['imageResults']:
                message.append('\n*Target image:* %s\n' % image_result['url'])
                for obj in image_result['objects']:
                    message.append('`%s:%s`' % (obj['class'],
                                                obj['confidence']))
        return '\n'.join(message)

    def run(self):
        is_raw_json = self.kwargs['--raw-json']
        job_id = self.kwargs['<job_id>']

        logging.info('GET /v2/find-object - job_id=%s' % job_id)
        try:
            response = self.ii_client.get_find_object_job(job_id)
        except ApiRequestError as e:
            logging.info(
                'failed to GET /v2/find-object - job_id=%s, error=%s' %
                (job_id, e))
            return

        if is_raw_json:
            self.slack_client.send_formatted_message(
                'OK `/find-object/%s` - JSON:' % response['id'],
                json.dumps(response, indent=2, sort_keys=True),
                self.kwargs['channel'], self.kwargs['user'])
        else:
            self.slack_client.send_formatted_message(
                None,
                self.parse_results(response),
                self.kwargs['channel'],
                self.kwargs['user'],
                is_code=False,
            )
