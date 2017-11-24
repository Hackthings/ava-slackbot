# -*- coding: utf-8 -*-


class Command:
    def __init__(self, config, **kwargs):
        self.kwargs = kwargs
        self.config = config

        self.run()

    def run(self):
        raise NotImplementedError
