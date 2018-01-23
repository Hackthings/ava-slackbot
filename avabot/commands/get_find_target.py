# -*- coding: utf-8 -*-
import logging
import json

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError


class GetFindTarget(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        user = self.kwargs['user']
        job_id = results['id']
        status = results['status']
        target_image = results['jobResults']['target']['images'][0]
        message = [f'<@{user}> OK `/find-target/{job_id}`']

        message.append(f'\n*Job Status:* {status}\n')
        message.append(f'\n*Target:* {target_image}\n')

        if results['status'] == 'COMPLETED_SUCCESSFULLY':
            if 'image' in results['jobResults']:
                res = results['jobResults']['image']['url']
            else:
                res = 'None'
            message.append(f'\n*Result:* {res}\n')

        return '\n'.join(message)

    def run(self):
        is_raw_json = self.kwargs['--raw-json']
        job_id = self.kwargs['<job_id>']
        channel = self.kwargs['channel']
        user = self.kwargs['user']

        logging.info(f'GET /v2/find-target - job_id={job_id}')
        try:
            response = self.ii_client.get_find_target_job(job_id)
        except ApiRequestError as e:
            logging.info(f'failed to GET /v2/find-target - job_id={job_id}, error={e}')
            return

        if is_raw_json:
            self.slack_client.send_formatted_message(f'OK `/find-target/{job_id}` - JSON:',
                                                     json.dumps(response, indent=2, sort_keys=True), channel, user)
        else:
            self.slack_client.send_formatted_message(None, self.parse_results(response), channel, user, is_code=False)
