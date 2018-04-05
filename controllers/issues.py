"""
Issue-related tasks
"""
from .common import BaseController
import parsers

import argparse, logging, re, time, sys

class IssueController(BaseController):
    def __init__(self, ghc):
        self.ghc = ghc

    def setup_argparse(self, subparsers):
        """
        Sets up the subparser for issue blaster
        """
        parser = subparsers.add_parser('issues', help='GitHub issue management tools')
        issue_subparsers = parser.add_subparsers(help='name of tool to execute')
        self.setup_blast_args(issue_subparsers)
        self.setup_copy_args(issue_subparsers)

    def setup_blast_args(self, subparsers):
        parser = subparsers.add_parser('blast', help='mass-create same issue for a list of GitHub users')
        parser.add_argument('csv', metavar='csv', type=str,
                            help='filename of the CSV containing a list of GitHub usernames')
        parser.add_argument('msg', metavar='markdown', type=str,
                            help='filename of file containing Markdown')
        parser.add_argument('title', metavar='title', type=str,
                            help='title for GitHub issue')
        parser.add_argument('-s', '--start-from', metavar='username', type=str,
                            help='start adding from a particular user (inclusive) in the CSV')
        parser.set_defaults(func=self.blast_command)

    def setup_copy_args(self, subparsers):
        help_text = 'copies issues from one repository to another'
        example_text = '''example:
  python main.py octocat/source octocat/destination
  python main.py -m mymapping.csv octocat/source octocat/destination
  python main.py -m mymapping.csv octocat/source octo{}/destination'''
        parser = subparsers.add_parser('copy',
                                 help=help_text,
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('fromrepo', metavar='from', type=str,
                            help='repository to copy from, in {owner}/{name} format')
        parser.add_argument('torepo', metavar='to', type=str,
                            help='repository to copy from, in {owner}/{name} format. If a replacement field ({}) is specified, it will be replaced with the first tag in the mapping.')
        parser.add_argument('-m', '--mapping', metavar='csv', type=str,
                            help='filename of CSV containing the title tag mapping')
        parser.add_argument('-s', '--start-from', metavar='index', type=int,
                            help='start copying from a particular index')
        parser.set_defaults(func=self.copy_command)

    def blast_command(self, args):
        logging.debug('Issue title: %s', args.title)
        logging.debug('CSV file: %s and MD file: %s', args.csv, args.msg)

        if parsers.common.are_files_readable(args.csv, args.msg):
            self.blast_issues(args.csv, args.title, args.msg, args.start_from)
        else:
            sys.exit(1)

    def copy_command(self, args):
        logging.debug('Copying from %s to %s', args.fromrepo, args.torepo)

        if args.mapping is None or parsers.common.are_files_readable(args.mapping):
            self.copy_issues(args.mapping, args.fromrepo, args.torepo, args.start_from)
        else:
            sys.exit(1)

    def copy_issues(self, mapping_file, fromrepo, torepo, offset):
        '''
        Copies issues from one repository to another
        '''
        first_repo_issues = self.ghc.get_issues_from_repository(fromrepo)
        mapping_dict = parsers.csvparser.get_rows_as_dict(mapping_file) if mapping_file is not None else {}
        REF_TEMPLATE = '\n\n<sub>[original: {}#{}]</sub>'

        if torepo.count('{}') > 1:
            logging.error('torepo contains more than 1 replacement field!')
            sys.exit(1)

        if not offset:
            offset = 0

        for idx, issue in enumerate(first_repo_issues[offset:]):
            from_mapping = re.search('\[(.*?)\]', issue.title)
            to_mapping = []
            new_title = issue.title.split(']', 1)[-1]
            new_body = issue.body + REF_TEMPLATE.format(fromrepo, issue.number)

            if from_mapping:
                from_mapping = from_mapping.group(1)
                to_mapping = mapping_dict.get(from_mapping, [])

            try:
                actl_to_repo = torepo.format(to_mapping[0])
            except IndexError:
                actl_to_repo = torepo.format('')

            is_transferred = self.ghc.create_issue(new_title, new_body, None, to_mapping, actl_to_repo)

            if not is_transferred:
                logging.error('[%d][#%d][%s -> %s] Unable to copy', idx, issue.number, fromrepo, actl_to_repo)

    def blast_issues(self, csv_file, title, msg_file, start_from):
        """
        Creates a unique issue with identical content for
        every GitHub user in a specified CSV file
        """
        user_tag_list = parsers.csvparser.get_rows_as_list(csv_file)
        user_list = [x[0] for x in user_tag_list]
        message = parsers.common.get_contents(msg_file)

        if start_from and start_from in user_list:
            user_tag_list = user_tag_list[user_list.index(start_from):]

        failed_users = []

        quota = self.ghc.get_remaining_quota()
        num_issues = min(quota, len(user_tag_list))

        if quota < len(user_tag_list):
            num_issues = quota
            print('Insufficient quota! Run again (when quota resets) from', user_list[quota], 'user onwards!')
            logging.warn('Insufficient API quota!')
            logging.warn('Creating issues for users up till: %s (Next user: %s)', user_tag_list[quota - 1][0],  user_tag_list[quota][0])

        logging.info('Creating issues for %d user(s)', num_issues)

        for (user, user_title, *labels) in user_tag_list[:num_issues]:
            final_title = title.format(user_title)
            is_created = self.ghc.create_issue(final_title, message, user, labels)
            if not is_created:
                logging.error('Unable to create issue for user: %s', user)
                failed_users.append(user)
            time.sleep(2) # ensures app is within abuse rate limit

        num_issues = len(user_tag_list) - len(failed_users)

        logging.info('Blasting completed! %d issues created!', num_issues)

        if len(failed_users) > 0:
            logging.warn('Unable to create issue for users: %s', failed_users)
