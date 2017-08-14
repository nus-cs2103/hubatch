import configparser
"""
Configuration information for app
"""

class AppConfig:
    def __init__(self, cfg_file='config.cfg'):
        self.config = configparser.ConfigParser()
        self.config.read(cfg_file)

        self.api_key = self.config.get('dev', 'APIKey')
        self.repo = self.config.get('dev', 'Repo')
        self.organisation = self.config.get('dev', 'Organisation')

    def get_api_key(self):
        return self.api_key

    def get_repo(self):
        return self.repo

    def get_organisation(self):
        return self.organisation
