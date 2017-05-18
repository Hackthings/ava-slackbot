# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import Dict


def docopt_arg_validator(arguments: Dict) -> Dict:
    args = deepcopy(arguments)

    if args['--head']:
        try:
            args['--head'] = int(args['--head'])
        except (ValueError, TypeError):
            raise ValueError('--head: number of top categories must be a valid integer')
        if args['--head'] <= 0:
            raise ValueError('--head: number of top categories must be greater than 0')
    return args
