from common.config import AppConfig

from connectors.github import GitHubConnector

import parsers

import argparse, sys, logging

logging.basicConfig(filename='log.log',level=logging.DEBUG)

cfg = AppConfig()
ghc = GitHubConnector(cfg.get_api_key(), cfg.get_repo())

def setup_argparse():
    """Sets up argparse"""
    parser = argparse.ArgumentParser(description='Blasts issues to a given list of users')
    parser.add_argument('csv', metavar='csv', type=str,
                        help='filename of the CSV containing a list of GitHub usernames')
    parser.add_argument('msg', metavar='markdown', type=str,
                        help='filename of file containing Markdown')
    parser.add_argument('title', metavar='title', type=str,
                        help='title for GitHub issue')
    return parser

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
    parser = setup_argparse()
    args = parser.parse_args()

    logging.debug('Issue title: %s', args.title)
    logging.debug('CSV file: %s and MD file: %s', args.csv, args.msg)

    if parsers.common.are_files_readable(args.csv, args.msg):
        blast_issues(args.csv, args.title, args.msg)
    else:
        sys.exit(1)
