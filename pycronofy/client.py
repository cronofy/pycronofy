import requests
from pycronofy import settings
from .auth import Auth
from .datetime_utils import get_iso8601_string
from .pagination import Pages

class CronofyClient(object):
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
        :return: Response.
        :rtype: ``response``
        """
        return self.auth.update_tokens_from_code(code)

    def close_notification_channel(self, channel_id):
        """Close a notification channel to stop push notifications from being sent.

        :param string channel_id: The id of the notification channel.
        :return: Response
        :rtype: ``response``
        """
        return self._delete(endpoint='channels/%s' % channel_id)

    def create_notification_channel(self, callback_url, calendar_ids=()):
        """Create a new channel for receiving push notifications.

        :param string callback_url: The url that will receive push notifications.
        Must not be longer than 128 characters and should be HTTPS.
        :return: Response
        :rtype: ``response``
        """
        data = {'callback_url': callback_url}
        if calendar_ids:
            data['filters'] = {'calendar_ids':calendar_ids}
        return self._post('channels', data=data)

    def delete_event(self, calendar_id, event_id):
        """Delete an event from the specified calendar.
        :param string calendar_id: ID of calendar to insert/update event into.
        :param string event_id: ID of event to delete.
        :return: Response from _delete
        :rtype: ``Response``
        """
        return self._delete(endpoint='calendars/%s/events' % calendar_id, params={'event_id': event_id})

    def list_calendars(self):
        """Return a list of calendars available for the active account.

        :return: List of calendars (dictionaries).
        :rtype: ``list``
        """
        calendars = self._get(endpoint='calendars')
        return calendars['calendars']

    def list_notification_channels(self):
        """Return a list of notification channels available for the active account.

        :return: List of notification channels (dictionaries).
        :rtype: ``list``
        """
        channels = self._get(endpoint='channels')
        return channels['channels']

    def read_events(self, 
        calendar_ids=(), 
        from_date=None, 
        to_date=None, 
        last_modified=None,
        tzid=settings.DEFAULT_TIMEZONE_ID, 
        only_managed=False,
        include_managed=True, 
        automatic_pagination=True):
        """Read events for linked account (optionally for the specified calendars).

        :param tuple calendar_ids: Tuple or list of calendar ids to pass to cronofy. (Optional).
        :param datetime.date from_date: Start datetime (or ISO8601 string) for query. (Optional).
        :param datetime.date to_date: End datetime (or ISO8601 string) for query. (Optional).
        :param datetime.datetime last_modified: Return items modified on or after last_modified. Datetime or ISO8601 string. (Optional).
        :param string tzid: Timezone ID for query. (Optional, default settings.DEFAULT_TIMEZONE_ID). Should match tzinfo on datetime objects.
        :param bool only_managed: Only include pages created through the API. (Optional, default False)
        :param bool include_managed: Include pages created through the API. (Optional, default True)
        :param bool automatic_pagination: Autonatically fetch next page when iterating through results (Optional, default True)
        :return: Wrapped results (Containing first page of events).
        :rtype: ``Pages``
        """
        events = self._get(endpoint='events', params={
            'tzid': tzid, 
            'calendar_ids':calendar_ids,
            'from': get_iso8601_string(from_date), 
            'to': get_iso8601_string(to_date),
            'last_modified': get_iso8601_string(last_modified),
            'only_managed': only_managed,
            'include_managed': include_managed,
        })
        return Pages(self, events, 'events', automatic_pagination)

    def refresh_access_token(self):
        """Refreshes the authorization token.

        :return: Response.
        :rtype: ``response``
        """
        return self.auth.refresh(code)

    def revoke_authorization(self):
        """Revokes Oauth authorization."""
        self.auth.revoke()

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
        event['start'] = get_iso8601_string(event['start'])
        event['end'] = get_iso8601_string(event['end'])
        return self._post(endpoint='calendars/%s/events' % calendar_id, data=event)

    def user_auth_link(self, redirect_uri, scope='', state=''):
        """Generates a URL to send the user for OAuth 2.0

        :param string redict_url: URL to redirect the user to after auth.
        :param string scope: The scope of the privileges you want the eventual access_token to grant.
        :param string state: A value that will be returned to you unaltered along with the user's authorization request decision.
        (The OAuth 2.0 RFC recommends using this to prevent cross-site request forgery.)
        :return: authorization link
        :rtype: ``string``
        """
        if not scope:
            scope = ' '.join(settings.DEFAULT_OAUTH_SCOPE)
        return self.auth.user_auth_link(redirect_uri, scope, state).url

    def _get(self, endpoint='', url='', params={}):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        return self._request(requests.get, endpoint, url, params=params, return_json=True)

    def _delete(self, endpoint='', url='', params={}):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        return self._request(requests.delete, endpoint, url, params=params)

    def _post(self, endpoint='', url='', data={}):
        """Perform a post to an API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :return: Response.
        :rtype: ``Response``
        """
        return self._request(requests.post, endpoint, url, data=data)

    def _request(self, request_method, endpoint='', url='', data={}, params={}, return_json=False):
        """Perform a http request via the specified method to an API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :param bool return_json: Return json instead of the Response object. (Optional, default False).
        :return: Response or Response json
        :rtype: ``Response`` or ``dict``
        """
        if endpoint and not url:
            url = '%s/%s/%s' % (settings.API_BASE_URL, settings.API_VERSION, endpoint)
        if data:
            response = request_method(url, headers={'Authorization': self.auth.get_authorization()}, json=data)
        else:
            response = request_method(url, headers={'Authorization': self.auth.get_authorization()}, params=params)
        # if response.status_code == requests.codes.unauthorized:
        #     #refresh
        #     pass
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        if return_json:
            return response.json()
        return response

