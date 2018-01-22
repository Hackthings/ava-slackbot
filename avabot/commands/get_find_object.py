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
        user = self.kwargs['user']
        job_id = results['id']
        status = results['status']
        message = [f'<@{user}> OK `/find-object/{job_id}`']
        message.append(f'\n*Job Status:* {status}\n')

        if results['status'] == "COMPLETED_SUCCESSFULLY":
            for image_result in results['imageResults']:
                img_result_url = image_result['url']
                message.append(f'\n*Target image:* {img_result_url}\n')
                for obj in image_result['objects']:
                    cls = obj['class']
                    cnf = obj['confidence']
                    message.append(f'`{cls}:{cnf}`')
        return '\n'.join(message)

    def run(self):
        is_raw_json = self.kwargs['--raw-json']
        job_id = self.kwargs['<job_id>']

        logging.info(f'GET /v2/find-object - job_id={job_id}')
        try:
            response = self.ii_client.get_find_object_job(job_id)
        except ApiRequestError as e:
            logging.info(f'failed to GET /v2/find-object - job_id={job_id}, error={e}')
            return

        if is_raw_json:
            self.slack_client.send_formatted_message(f'OK `/find-object/{job_id}` - JSON:',
                                                     json.dumps(response, indent=2, sort_keys=True),
                                                     self.kwargs['channel'], self.kwargs['user'])
        else:
            self.slack_client.send_formatted_message(
                None, self.parse_results(response), self.kwargs['channel'], self.kwargs['user'], is_code=False)
