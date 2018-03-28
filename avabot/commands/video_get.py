# -*- coding: utf-8 -*-
import logging

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError


class VideoGet(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        user = self.kwargs['user']
        job_id = results['id']
        status = results['status']
        video = results['video']
        message = [f'<@{user}> OK `/video/{job_id}`']

        message.append(f'\n*Job Status:* {status}\n')

        message.append(f'\n*Video:* {video}\n')

        if status == 'COMPLETED_SUCCESSFULLY':
            if len(results['jobResults']) > 0:
                res = results['jobResults'][0]['image']['url']
            else:
                res = 'None'
            message.append(f'\n*Result:* {res}\n')

        return '\n'.join(message)

    def request(self):
        job_id = self.kwargs['<job_id>']

        logging.info(f'GET /v2/video - job_id={job_id}')
        try:
            return self.ii_client.get_video_job(job_id)
        except ApiRequestError as e:
            logging.info(f'failed to GET /v2/video - job_id={job_id}, error={e}')
            raise
