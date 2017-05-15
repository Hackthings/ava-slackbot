# -*- coding: utf-8 -*-
from ..config import Config


class Command(object):
    def __init__(self, config: Config, **kwargs) -> None:
        self.kwargs = kwargs
        self.config = config

        self.run()

    def run(self) -> None:
        raise NotImplementedError
