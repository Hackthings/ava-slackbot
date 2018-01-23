# -*- coding: utf-8 -*-
import json


class Command:
    def __init__(self, config, **kwargs):
        self.config = config
        self.kwargs = kwargs

        self.run()

    def run(self):
        # execute api call
        response = self.request()

        channel = self.kwargs['channel']
        user = self.kwargs['user']
        is_raw_json = self.kwargs['--raw-json']

        # send reply
        if is_raw_json:
            self.slack_client.send_formatted_message('OK - JSON response:',
                                                     json.dumps(response, indent=2, sort_keys=True), channel, user)
        else:
            self.slack_client.send_formatted_message(None, self.parse_results(response), channel, user, is_code=False)
