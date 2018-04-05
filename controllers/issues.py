"""
Issue-related tasks
"""
from .common import BaseController
import parsers

import logging, re, time, sys

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
        parser = subparsers.add_parser('copy', help='copies issues from one repository to another')
        parser.add_argument('fromrepo', metavar='from', type=str,
                            help='repository from which we should copy')
        parser.add_argument('torepo', metavar='to', type=str,
                            help='repository to which we should copy to')
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

        if parsers.common.are_files_readable(args.mapping):
            self.copy_issues(args.mapping, args.fromrepo, args.torepo, args.start_from)
        else:
            sys.exit(1)

    def copy_issues(self, mapping_file, fromrepo, torepo, offset):
        '''
        Copies issues from one repository to another
        '''
        first_repo_issues = self.ghc.get_issues_from_repository(fromrepo)
        mapping_dict = parsers.csvparser.get_rows_as_dict(mapping_file)
        REF_TEMPLATE = '\n\n<sub>[original: {}#{}]</sub>'

        if not offset:
            offset = 0

        for idx, issue in enumerate(first_repo_issues[offset:]):
            from_mapping = re.search('\[(.*?)\]', issue.title)
            to_mapping = []
            new_title = issue.title.split(']', 1)[-1]
            new_body = issue.body + REF_TEMPLATE.format(fromrepo, issue.number)

            if from_mapping:
                from_mapping = from_mapping.group(1)
                print(from_mapping)
                to_mapping = mapping_dict.get(from_mapping, from_mapping)

            is_transferred = self.ghc.create_issue(new_title, new_body, None, to_mapping, torepo)

            if not is_transferred:
                logging.error('Unable to create issue with idx: %s', user)

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
