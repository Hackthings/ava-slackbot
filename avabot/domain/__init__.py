# -*- coding: utf-8 -*-


class AvaSlackbotException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
