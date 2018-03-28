# -*- coding: utf-8 -*-
import uuid
import logging

from avabot.commands import Command
from avabot.exceptions.imageintelligence import ApiRequestError
from avabot.constants import DEFAULT_CLASS, DEFAULT_FPS


class Video(Command):
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
        video_url = self.kwargs['<url>']
        classes = self.kwargs['--class'] or [DEFAULT_CLASS]
        fps = self.kwargs['--fps'] or DEFAULT_FPS

        classes = [{'class': cls} for cls in classes]

        logging.info(f'posting to /v2/video - url={video_url}')

        try:
            response = self.ii_client.video(video_url, fps, classes, custom_id='ava-slackbot-' + str(uuid.uuid4()))
            result = self.ii_client.poll_for_video_result(response['id'])
        except ApiRequestError as e:
            logging.info(f'failed to POST /v2/video - urls={video_url}, error={e}')
            raise e

        logging.info(f'successfully POST\'d to /v2/video')
        return result
