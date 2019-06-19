class Auth(object):
    """
    Hold OAuth/Access Data, convenience methods.

    https://www.cronofy.com/developers/api/#authentication
    """

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None, token_expiration=None):
        """
        :param string client_id: OAuth Client ID. (Optional, default None)
        :param string client_secret: OAuth Client Secret. (Optional, default None)
        :param string access_token: Access Token for User's Account. (Optional, default None)
        :param string refresh_token: Existing Refresh Token for User's Account. (Optional, default None)
        :param datetime.datetime token_expiration: Datetime token expires. (Optional, default None)
        :param bool settings.DEBUG: Instantiate in debug mode. (Optional, default False).
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiration = token_expiration
        self.redirect_uri = ''

    def get_authorization(self):
        """Get the authorization header with the currently active token

        :return: 'Authorization' header
        :rtype: ``string``
        """
        return 'Bearer %s' % self.access_token

    def get_api_key(self):
        """Get the authorization header with the api key token

        :return: 'Authorization' header
        :rtype: ``string``
        """
        return 'Bearer %s' % self.client_secret

    def update(self, **kwargs):
        """Update fields

        :param KeywordArguments kwargs: Fields and values to update.
        """
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
