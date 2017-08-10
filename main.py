from common.config import AppConfig

from connectors.github import GitHubConnector

import parsers

import argparse, logging, sys, time

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
    parser.add_argument('-s', '--start-from', metavar='username', type=str,
                        help='start adding from a particular user (inclusive) in the CSV')
    return parser

def prompt_user():
    """
    Prompts the user for filenames containing data
    """
    csv = input('Filename of CSV with GitHub IDs:')
    msg = input('Filename of file containing issue message:')

    return csv, msg

def blast_issues(csv_file, title, msg_file, start_from):
    """
    Creates a unique issue with identical content for
    every GitHub user in a specified CSV file
    """
    user_list = parsers.csvparser.get_rows_as_list(csv_file)
    message = parsers.common.get_contents(msg_file)

    if start_from and start_from in user_list:
        user_list = user_list[user_list.index(start_from):]

    failed_users = []

    quota = ghc.get_remaining_quota()
    num_issues = min(quota, len(user_list))

    if quota < len(user_list):
        num_issues = quota
        print('Insufficient quota! Run again (when quota resets) from', user_list[quota], 'user onwards!')
        logging.warn('Insufficient API quota!')
        logging.warn('Creating issues for users up till: %s (Next user: %s)', user_list[quota - 1],  user_list[quota])

    logging.info('Creating issues for %d user(s)', num_issues)

    for user, label in user_list[:num_issues]:
        is_created = ghc.create_issue(title, message, user, [label])
        if not is_created:
            logging.error('Unable to create issue for user: %s', user)
            failed_users.append(user)
        time.sleep(2) # ensures app is within abuse rate limit

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
        blast_issues(args.csv, args.title, args.msg, args.start_from)
    else:
        sys.exit(1)
