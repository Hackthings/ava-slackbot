# -*- coding: utf-8 -*-
import random
import string


def gen_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
