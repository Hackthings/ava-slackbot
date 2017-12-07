# -*- coding: utf-8 -*-
from avabot.exceptions import AvaSlackbotException


class UnknownAuthenticationError(AvaSlackbotException):
    pass


class InvalidClientCredentialsError(AvaSlackbotException):
    pass


class InvalidAccessTokenError(AvaSlackbotException):
    pass


class ApiRequestError(AvaSlackbotException):
    pass


class ApiRequestTimeoutError(AvaSlackbotException):
    pass
