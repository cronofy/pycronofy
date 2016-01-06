class Auth:
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
        if access_token:
            self._token = access_token

    def get_authorization(self):
        """Get the authorization header with the currently active token
        :return: 'Authorization' header
        :rtype: ``string``
        """
        return 'Bearer %s' % self._token
