# -*- coding: utf-8 -*-


class Command:
    def __init__(self, config, **kwargs):
        self.config = config
        self.kwargs = kwargs

        self.run()

    def run(self):
        raise NotImplementedError
