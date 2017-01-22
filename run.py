# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
from slackbot.bot import Bot


def main():
    logging.basicConfig()

    bot = Bot()
    print('bot running... ready to accept messages')
    bot.run()

if __name__ == '__main__':
    main()
