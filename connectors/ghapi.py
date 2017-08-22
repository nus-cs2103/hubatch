import requests

import logging

class GHAPI:
    """Class with static methods for calling up API"""
    BASE_URL = 'https://api.github.com'

    @classmethod
    def handle_api_exception(cls, request):
        json_resp = None

        if request is not None:
            try:
                json_resp = request.json()
            except ValueError as e:
                json_Resp = None

        logging.error('Exception raised by API! Response: %s', json_resp)

    @classmethod
    def invite_user(cls, api_key, organisation, username):
        """Invites a particular user to an organisation"""
        url = '{}/orgs/{}/memberships/{}'.format(cls.BASE_URL, organisation, username)
        auth_tuple = ('token', api_key)
        r = None
        try:
            r = requests.put(url, auth=auth_tuple)
        except requests.exceptions.RequestException as e:
            cls.handle_api_exception(None)
            return False

        try:
            r.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            cls.handle_api_exception(r)
            return False

    @classmethod
    def invite_user_team(cls, api_key, team_id, username):
        """Invites a particular user to a team"""
        url = '{}/teams/{}/memberships/{}'.format(cls.BASE_URL, team_id, username)
        auth_tuple = ('token', api_key)
        r = None
        try:
            r = requests.put(url, auth=auth_tuple)
        except requests.exceptions.RequestException as e:
            cls.handle_api_exception(None)
            return False

        try:
            r.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            cls.handle_api_exception(r)
            return False
