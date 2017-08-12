"""
Useful tools for managing organisations
"""
class OrganisationController:
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
        parser = subparsers.add_parser('mass-add', help='mass add a list of GitHub users')
        parser.add_argument('csv', metavar='csv', type=str,
                            help='filename of the CSV containing a list of GitHub usernames')
        parser.add_argument('-s', '--start-from', metavar='username', type=str,
                            help='start adding from a particular user (inclusive) in the CSV')
        parser.set_defaults(func=self.mass_add_command)

    def mass_add_command(self, args):
        pass
