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

    def get_api_key(self):
        return self.api_key

    def get_repo(self):
        return self.repo
