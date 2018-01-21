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
        message = [
            '<@%s> OK `/find-target/%s`' % (self.kwargs['user'],
                                            results['id']),
        ]
        message.append('\n*Job Status:* %s\n' % results['status'])
        message.append(
            '\n*Target:* %s\n' % results['jobResults']['target']['images'][0])
        if results['status'] == "COMPLETED_SUCCESSFULLY":
            if 'image' in results['jobResults']:
                res = results['jobResults']['image']['url']
            else:
                res = "None"
            message.append('\n*Result:* %s\n' % res)

        return '\n'.join(message)

    def run(self):
        print(self.kwargs)
        is_raw_json = self.kwargs['--raw-json']
        job_id = self.kwargs['<job_id>']

        logging.info('GET /v2/find-target - job_id=%s' % job_id)
        try:
            response = self.ii_client.get_find_target_job(job_id)
        except ApiRequestError as e:
            logging.info(
                'failed to GET /v2/find-target - job_id=%s, error=%s' %
                (job_id, e))
            return

        if is_raw_json:
            self.slack_client.send_formatted_message(
                'OK `/find-target/%s` - JSON:' % response['id'],
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
