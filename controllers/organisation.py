"""
Useful tools for managing organisations
"""
from .common import BaseController
import parsers

import logging, time

class OrganisationController(BaseController):
    def __init__(self, ghc):
        self.ghc = ghc

    def setup_argparse(self, subparsers):
        """
        Sets up the subparser for issue blaster
        """
        parser = subparsers.add_parser('orgs', help='GitHub organisation management tools')
        org_subparsers = parser.add_subparsers(help='name of tool to execute')
        self.setup_mass_add(org_subparsers)

    def setup_mass_add(self, subparsers):
        parser = subparsers.add_parser('mass-add', help='mass invite GitHub users into an organisation')
        parser.add_argument('csv', metavar='csv', type=str,
                            help='filename of the CSV containing a list of GitHub usernames')
        parser.add_argument('-s', '--start-from', metavar='username', type=str,
                            help='start adding from a particular user (inclusive) in the CSV')
        parser.add_argument('-t', '--team', metavar='team-id', type=int,
                            help='invites user to the particular team')
        parser.set_defaults(func=self.mass_add_command)

    def mass_add_command(self, args):
        logging.debug('Adding users to organisation')
        logging.debug('User CSV file: %s', args.csv)

        if parsers.common.are_files_readable(args.csv):
            self.add_users_from_csv(args.csv, args.start_from, args.team)
        else:
            sys.exit(1)

    def add_users_from_csv(self, csv_file, start_from, teamid):
        user_list = parsers.csvparser.get_rows_as_list(csv_file)
        user_list = [x for (x,) in user_list]

        if start_from and start_from in user_list:
            user_list = user_list[user_list.index(start_from):]

        for usr in user_list:
            is_created = False
            if not teamid:
                is_created = self.ghc.add_user_to_organisation(usr)
            else:
                is_created = self.ghc.add_user_to_team(usr, teamid)

            if not is_created:
                logging.warn('Unable to invite user %s. Stopping.', usr)
                print('Restart script from user:', usr)
                break
            time.sleep(2)
