import datetime
import requests
from pycronofy import settings

class Auth(object):
    """
    Handle authorization with Cronofy services via Personal Token and OAuth

    https://www.cronofy.com/developers/api/#authentication
    """

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None):
        """
        :param string client_id: OAuth Client ID.
        :param string client_secret: OAuth Client Secret.
        :param string access_token: Access Token for User's Account.
        :param string refresh_token: Existing Refresh Token for User's Account.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = 0
        self.authorization_datetime = datetime.datetime.now()
        self.redirect_uri = ''

    def get_authorization(self):
        """Get the authorization header with the currently active token

        :return: 'Authorization' header
        :rtype: ``string``
        """
        return 'Bearer %s' % self.access_token

    def refresh(self):
        """Refreshes the authorization token.

        :return: "Expires in".
        :rtype: ``int``
        """
        url = '%s/oauth/token' % settings.API_BASE_URL
        response = requests.post(url, json={
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            })
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        self.authorization_datetime = datetime.datetime.now()  
        data = response.json()
        self.access_token = data['access_token']
        self.expires_in = data['expires_in']
        return self.expires_in

    def revoke(self):
        """Revokes Oauth authorization."""
        url = '%s/oauth/token/revoke' % settings.API_BASE_URL
        response = requests.post(url, json={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'token': self.access_token,
            })
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        self.access_token = None
        self.refresh_token = None
        self.expires_in = 0

    def update_tokens_from_code(self, code):
        """Updates the authorization tokens from the user provided code.

        :param string code: Authorization code to pass to Cronofy.

        :return: "Expires in".
        :rtype: ``int``
        """
        url = '%s/oauth/token' % settings.API_BASE_URL
        response = requests.post(url, json={
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            })
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        self.authorization_datetime = datetime.datetime.now()  
        data = response.json()
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expires_in = data['expires_in']
        return self.expires_in

    def user_auth_link(self, redirect_uri, scope, state=''):
        """Generates a URL to send the user for OAuth 2.0

        :param string redict_url: URL to redirect the user to after auth.
        :param string scope: The scope of the privileges you want the eventual access_token to grant.
        :param string state: A value that will be returned to you unaltered along with the user's authorization request decision.
        (The OAuth 2.0 RFC recommends using this to prevent cross-site request forgery.)
        :return: authorization link
        :rtype: ``string``
        """
        url = '%s/oauth/authorize' % settings.APP_BASE_URL
        self.redirect_uri = redirect_uri
        response = requests.get(url, params={
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state,
            })
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response