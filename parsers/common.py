"""
Common File I/O methods
"""
import os

def are_files_readable(*filenames):
    """
    Checks if ALL files specified are
    readable by the running application
    """
    clean_so_far = True

    for filename in filenames:
        if not os.access(filename, os.R_OK):
            print('File', filename, 'is not readable!')
            clean_so_far = False

    return clean_so_far

def get_contents(filename):
    """Retrieves contents of a given file"""
    with open(filename, encoding="utf-8") as f:
        return f.read()
