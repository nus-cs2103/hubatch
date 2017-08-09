from common.config import AppConfig
from common import utils

from connectors.github import GitHubConnector

import parsers

import sys, logging

logging.basicConfig(filename='log.log',level=logging.DEBUG)

cfg = AppConfig()
ghc = GitHubConnector(cfg.get_api_key(), cfg.get_repo())

def prompt_user():
    """
    Prompts the user for filenames containing data
    """
    csv = input('Filename of CSV with GitHub IDs:')
    msg = input('Filename of file containing issue message:')

    return csv, msg

def blast_issues(csv_file, title, msg_file):
    """
    Creates a unique issue with identical content for
    every GitHub user in a specified CSV file
    """
    user_list = parsers.csvparser.get_rows_as_list(csv_file)
    message = parsers.common.get_contents(msg_file)

    failed_users = []

    quota = ghc.get_remaining_quota()
    num_issues = min(quota, len(user_list))

    if quota < len(user_list):
        num_issues = quota
        logging.warn('Insufficient API quota!')
        logging.warn('Creating issues for users up till: %s', user_list[quota - 1])

    logging.info('Creating issues for %d user(s)', num_issues)

    for user in user_list[:num_issues]:
        is_created = ghc.create_issue(title, message, user)
        if not is_created:
            logging.error('Unable to create issue for user: %s', user)
            failed_users.append(user)

    num_issues = len(user_list) - len(failed_users)

    logging.info('Blasting completed! %d issues created!', num_issues)

    if len(failed_users) > 0:
        logging.warn('Unable to create issue for users: %s', failed_users)

if __name__ == '__main__':
    logging.info('Kena Arrowed - GitHub issue manager started!')
    csv, msg, title = utils.get_arguments(3)

    if not (csv or msg):
        csv, msg = prompt_user()

    if not title:
        title = 'An Issue'

    logging.debug('Issue title: %s', title)
    logging.debug('CSV file: %s and MD file: %s', csv, msg)

    if parsers.common.are_files_readable(csv, msg):
        blast_issues(csv, title, msg)
    else:
        sys.exit(1)
