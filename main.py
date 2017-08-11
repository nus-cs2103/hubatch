from app.issues import IssueController
from common.config import AppConfig
from connectors.github import GitHubConnector

import parsers

import argparse, logging, sys

logging.basicConfig(filename='log.log',level=logging.DEBUG)

cfg = AppConfig()
ghc = GitHubConnector(cfg.get_api_key(), cfg.get_repo())
issue_ctrl = IssueController(ghc)

def setup_argparse():
    """Sets up argparse"""
    parser = argparse.ArgumentParser(description='useful command line tools for GitHub')
    subparsers = parser.add_subparsers(help='name of tool to run')
    issue_ctrl.setup_argparse(subparsers)
    return parser

if __name__ == '__main__':
    logging.info('Kena Arrowed - GitHub issue manager started!')
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)
