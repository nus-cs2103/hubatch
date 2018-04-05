from github import Github, GithubObject, GithubException
from .ghapi import GHAPI

import logging

class GitHubConnector:
    def __init__(self, apikey, repo, org):
        try:
            self.api_key = apikey
            self.gh = Github(apikey)
            self.repo = self.gh.get_repo(repo)
            self.labels = self.get_labels()
            self.organisation = self.gh.get_organization(org)
        except GithubException as e:
            GitHubConnector.log_exception(e.data)

    def log_exception(info):
        logging.error('Exception raised by GitHub API!')
        logging.error('Response from API: %s', info)

    def is_api_available(self):
        ratelimit = self.gh.get_rate_limit()
        logging.debug('API Quota: %d out of %d', ratelimit.rate.remaining, ratelimit.rate.limit)
        return True if ratelimit.rate.remaining > 0 else False

    def get_labels(self):
        """Load & cache labels from the repository"""
        try:
            return self.repo.get_labels()
        except GithubException as e:
            GitHubConnector.log_exception(e.data)
            return []

    def has_label(self, lbl):
        """Checks if repo contains a label with the same name"""
        return any(lbl_obj.name == lbl for lbl_obj in self.labels)

    def str_to_label(self, lbl):
        """Converts a label name to a label object"""
        return next((lbl_obj for lbl_obj in self.labels if lbl_obj.name == lbl), None)

    def strs_to_labels(self, strs):
        """Converts a list of label names to their respective label objects"""
        return [self.str_to_label(lbl) for lbl in strs if self.has_label(lbl)]

    def get_remaining_quota(self):
        ratelimit = self.gh.get_rate_limit()
        return ratelimit.rate.remaining

    def get_issues(self):
        """Gets all issues in a given repository"""
        try:
            return self.repo.get_issues()
        except GithubException as e:
            GitHubConnector.log_exception(e.data)
            return []

    def get_issues_from_repository(self, repo_name):
        '''Gets issues from a specified repository'''
        try:
            repo = self.gh.get_repo(repo_name)
            return repo.get_issues(direction='asc')
        except GithubException as e:
            GitHubConnector.log_exception(e.data)
            return []

    def create_issue(self, title, msg, assignee, labels=[], repo=None):
        """Creates an Issue in a given repository"""
        if not self.is_api_available():
            return False
        elif assignee is None:
            assignee = GithubObject.NotSet

        logging.info('Creating issue %s for %s', title, assignee)
        lbl_objs = self.strs_to_labels(labels)

        try:
            repo_obj = self.repo
            if repo is not None:
               repo_obj = self.gh.get_repo(repo)
            issue = repo_obj.create_issue(title, body=msg, assignee=assignee,
                                          labels=lbl_objs)
            logging.info('Issue created as #%s', issue.id)
            return True
        except GithubException as e:
            GitHubConnector.log_exception(e.data)
            if assignee is GithubObject.NotSet:
                return False
            else:
                # try without assignee
                return self.create_issue(title, msg, None, labels)

    def add_user_to_organisation(self, user):
        """Add a user to an organisation as a member"""
        if not self.is_api_available():
            return False

        logging.info('Inviting user %s to %s', user, self.organisation.login)

        return GHAPI.invite_user(self.api_key, self.organisation.login, user)

    def add_user_to_team(self, user, teamid):
        """Add a user to a team as a member"""
        if not self.is_api_available():
            return False

        logging.info('Inviting user %s to team id: %s', user, teamid)

        return GHAPI.invite_user_team(self.api_key, teamid, user)
