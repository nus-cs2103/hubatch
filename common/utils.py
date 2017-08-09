"""
App-wide utility methods
"""

import sys

def get_arguments(len, default=None):
    """
    Return first len number of argv values with defaults
    """
    rtn_lst = [default]*len

    for idx, arg in enumerate(sys.argv[1:]):
        if idx == len:
            return rtn_lst
        rtn_lst[idx] = arg

    return rtn_lst
