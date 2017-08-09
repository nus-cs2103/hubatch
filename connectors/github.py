from github import Github, GithubException

import logging

class GitHubConnector:
    def __init__(self, apikey, repo):
        try:
            self.gh = Github(apikey)
            self.repo = self.gh.get_repo(repo)
        except GithubException as e:
            GitHubConnector.log_exception(e.data)

    def log_exception(info):
        logging.error('Exception raised by GitHub API!')
        logging.error('Response from API: %s', info)

    def is_api_available(self):
        ratelimit = self.gh.get_rate_limit()
        logging.debug('API Quota: %d out of %d', ratelimit.rate.remaining, ratelimit.rate.limit)
        return True if ratelimit.rate.remaining > 0 else False

    def get_remaining_quota(self):
        ratelimit = self.gh.get_rate_limit()
        return ratelimit.rate.remaining

    def create_issue(self, title, msg, assignee):
        """Creates an Issue in a given repository"""
        if not self.is_api_available():
            return False

        logging.info('Creating issue %s for %s', title, assignee)

        try:
            issue = self.repo.create_issue(title, body=msg, assignee=assignee)
            logging.info('Issue created as #%s', issue.id)
            return True
        except GithubException as e:
            GitHubConnector.log_exception(e.data)
