# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from slackbot.bot import respond_to
from slackbot.bot import listen_to


@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('I can understand hi or HI!')
    message.react('+1')


@respond_to('I love you')
def love(message):
    message.reply('I love you too!')


@respond_to('Denise')
def denise(message):
    message.reply('Denise is really really awesome')


@listen_to('Can someone help me?')
def help(message):
    message.reply('Yes, I can!')
