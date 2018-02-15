# -*- coding: utf-8 -*-
import logging

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError


class DetectGet(Command):
    def __init__(self, config, ii_client, slack_client, **kwargs):
        self.ii_client = ii_client
        self.slack_client = slack_client

        super().__init__(config, **kwargs)

    def parse_results(self, results):
        user = self.kwargs['user']
        job_id = results['id']
        status = results['status']
        message = [f'<@{user}> OK `/detect/{job_id}`']
        message.append(f'\n*Job Status:* {status}\n')

        if results['status'] == 'COMPLETED_SUCCESSFULLY':
            for image_result in results['imageResults']:
                img_result_url = image_result['url']
                message.append(f'\n*Target image:* {img_result_url}\n')
                for obj in image_result['objects']:
                    cls = obj['class']
                    cnf = obj['confidence']
                    message.append(f'`{cls}:{cnf}`')
        return '\n'.join(message)

    def request(self):
        job_id = self.kwargs['<job_id>']

        logging.info(f'GET /v2/detect - job_id={job_id}')
        try:
            return self.ii_client.get_detect_job(job_id)
        except ApiRequestError as e:
            logging.info(f'failed to GET /v2/detect - job_id={job_id}, error={e}')
            return
