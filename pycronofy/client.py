import requests
from pycronofy import settings
from .auth import Auth
from .datetime_utils import get_datetime_string
from .pagination import Pages

class CronofyClient:
    """Client for cronofy web service.
    Performs authentication, and wraps API: https://www.cronofy.com/developers/api/
    """

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None):
        """
        Example Usage:

        CronofyClient(access_token='')
        CronofyClient(client_id='', client_secret='')

        :param string client_id: OAuth Client ID.
        :param string client_secret: OAuth Client Secret.
        :param string access_token: Access Token for User's Account.
        :param string refresh_token: Existing Refresh Token for User's Account.
        """
        self.auth = Auth(client_id, client_secret, access_token, refresh_token)

    def authorize_from_code(self, code):
        """Updates the authorization from the user provided code.

        :param string code: Authorization code to pass to Cronofy.

        :return: "Expires In".
        :rtype: ``int``
        """
        return self.auth.update_tokens_from_code(code)

    def list_calendars(self):
        """Return a list of calendars available for the active account.

        :return: List of calendars (dictionaries).
        :rtype: ``list``
        """
        calendars = self._get(endpoint='calendars')
        return calendars['calendars']

    def read_events(self, 
        calendar_ids=(), 
        from_date=None, 
        to_date=None, 
        tzid=settings.DEFAULT_TIMEZONE_ID, 
        include_managed=True, 
        automatic_pagination=True):
        """Read events for linked account (optionally for the specified calendars).

        :param tuple calendar_ids: Tuple or list of calendar ids to pass to cronofy. (Optional).
        :param datetime.datetime from_date: Start datetime (or ISO8601 string) for query. (Optional).
        :param datetime.datetime to_date: End datetime (or ISO8601 string) for query. (Optional).
        :param string tzid: Timezone ID for query. (Optional, default settings.DEFAULT_TIMEZONE_ID). Should match tzinfo on datetime objects.
        :param bool include_managed: Include pages created through the API. (Optional, default True)
        :param bool automatic_pagination: Autonatically fetch next page when iterating through results (Optional, default True)
        :return: Wrapped results (Containing first page of events).
        :rtype: ``Pages``
        """
        events = self._get(endpoint='events', params={
            'tzid': tzid, 
            'calendar_ids':calendar_ids,
            'from': get_datetime_string(from_date), 
            'to': get_datetime_string(to_date),
            'include_managed':True,
            })
        return Pages(self, events, 'events', automatic_pagination)

    def upsert_event(self, calendar_id, event):
        """
        :param string calendar_id: ID of calendar to insert/update event into.
        :param dict event: Dictionary of event data to send to cronofy.
        :return: Response from _post
        :rtype: ``Response``
        """
        for key in settings.EVENTS_REQUIRED_FIELDS:
            if not key in event:
                raise Exception('%s not found in event.' % key)
        event['start'] = get_datetime_string(event['start'])
        event['end'] = get_datetime_string(event['end'])
        return self._post(endpoint='calendars/%s/events' % calendar_id, data=event)

    def user_auth_link(self, redirect_uri, scope='', state=''):
        """Generates a URL to send the user for OAuth 2.0

        :param string redict_url: meow
        :param string scope: The scope of the privileges you want the eventual access_token to grant.
        :param string state: A value that will be returned to you unaltered along with the user's authorization request decision.
        (The OAuth 2.0 RFC recommends using this to prevent cross-site request forgery.)
        :return: authorization link
        :rtype: ``string``
        """
        if not scope:
            scope = ' '.join(settings.DEFAULT_OAUTH_SCOPE)
        return self.auth.user_auth_link(redirect_uri, scope, state)

    def _get(self, endpoint='', url='', params={}):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        if endpoint and not url:
            url = '%s/%s/%s' % (settings.API_BASE_URL, settings.API_VERSION, endpoint)
        response = requests.get(url, headers={'Authorization': self.auth.get_authorization()}, params=params)
        if response.status_code == requests.codes.unauthorized:
            #refresh
            pass
        elif response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response.json()

    def _post(self, endpoint='', url='', data={}):
        """Perform a post to an API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :return: Response.
        :rtype: ``Response``
        """
        if endpoint and not url:
            url = '%s/%s/%s' % (settings.API_BASE_URL, settings.API_VERSION, endpoint)
        response = requests.post(url, headers={'Authorization': self.auth.get_authorization()}, json=data)
        if response.status_code == requests.codes.unauthorized:
            #refresh
            pass
        elif response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response
