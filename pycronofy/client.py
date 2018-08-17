import datetime
import collections
from future.standard_library import hooks

from pycronofy import settings
from pycronofy.auth import Auth
from pycronofy.batch import BatchEntry
from pycronofy.batch import BatchResponse
from pycronofy.datetime_utils import format_event_time
from pycronofy.exceptions import PyCronofyPartialSuccessError
from pycronofy.pagination import Pages
from pycronofy.request_handler import RequestHandler
from pycronofy.validation import validate

with hooks():
    from urllib.parse import urlencode


class Client(object):
    """Client for cronofy web service.
    Performs authentication, and wraps API: https://www.cronofy.com/developers/api/
    """

    def __init__(self, client_id=None, client_secret=None, access_token=None, refresh_token=None, token_expiration=None, data_center=None):
        """
        Example Usage:

        pycronofy.Client(access_token='')
        pycronofy.Client(client_id='', client_secret='')

        :param string client_id: OAuth Client ID. (Optional, default None)
        :param string client_secret: OAuth Client Secret. (Optional, default None)
        :param string access_token: Access Token for User's Account. (Optional, default None)
        :param string refresh_token: Existing Refresh Token for User's Account. (Optional, default None)
        :param string token_expiration: Datetime token expires. (Optional, default None)
        :param string data_center: The name of the data_center to use. (Optional, default None)
        """
        self.auth = Auth(client_id, client_secret, access_token,
                         refresh_token, token_expiration)
        self.request_handler = RequestHandler(self.auth, data_center)

        if data_center is None or data_center is 'us':
            self.app_base_url = settings.APP_BASE_URL
        else:
            self.app_base_url = settings.APP_REGION_FORMAT % data_center

    def account(self):
        """Get identifying information for the active account.

        :return: Account data.
        :rtype: ``dict``
        """
        return self.request_handler.get(endpoint='account').json()['account']

    def userinfo(self):
        """Retrieves the userinfo for the account

        See http://openid.net/specs/openid-connect-core-1_0.html#UserInfo for
        reference

        :return: Userinfo data.
        :rtype: ``dict``
        """
        return self.request_handler.get(endpoint='userinfo').json()

    def close_notification_channel(self, channel_id):
        """Close a notification channel to stop push notifications from being sent.

        :param string channel_id: The id of the notification channel.
        """
        self.request_handler.delete(endpoint='channels/%s' % channel_id)

    def change_participation_status(self, calendar_id, event_uid, status):
        """Changes the participation status for a calendar event

        :param string calendar_id: The String Cronofy ID for the calendar to delete the event from.
        :param string event_uid: A String uniquely identifying the event for your
        application (note: this is NOT an ID generated by Cronofy).
        :param string status: A String to set the participation status of the event to
        :return: None
        """
        data = {'status': status}

        self.request_handler.post('calendars/%s/events/%s/participation_status' % (calendar_id, event_uid), data=data)

    def create_notification_channel(self, callback_url, calendar_ids=()):
        """Create a new channel for receiving push notifications.

        :param string callback_url: The url that will receive push notifications.
        Must not be longer than 128 characters and should be HTTPS.
        :param tuple calendar_ids: List of calendar ids to create notification channels for. (Optional. Default empty tuple)
        :return: Channel id and channel callback
        :rtype: ``dict``
        """
        data = {'callback_url': callback_url}
        if calendar_ids:
            data['filters'] = {'calendar_ids': calendar_ids}

        return self.request_handler.post('channels', data=data).json()['channel']

    def delete_all_events(self, calendar_ids=()):
        """Deletes all events managed through Cronofy from the all of the user's calendars.

        :param tuple calendar_ids: List of calendar ids to delete events for. (Optional. Default empty tuple)
        """
        params = {'delete_all': True}
        if calendar_ids:
            params = {'calendar_ids[]': calendar_ids}

        self.request_handler.delete(endpoint='events', params=params)

    def delete_event(self, calendar_id, event_id):
        """Delete an event from the specified calendar.

        :param string calendar_id: ID of calendar to delete from.
        :param string event_id: ID of event to delete.
        """
        self.request_handler.delete(endpoint='calendars/%s/events' % calendar_id, data={'event_id': event_id})

    def delete_external_event(self, calendar_id, event_uid):
        """Delete an external event from the specified calendar.

        :param string calendar_id: ID of calendar to delete from.
        :param string event_uid: ID of event to delete.
        """
        self.request_handler.delete(endpoint='calendars/%s/events' % calendar_id, data={'event_uid': event_uid})

    def elevated_permissions(self, permissions, redirect_uri=None):
        """Requests elevated permissions for a set of calendars.

        :param tuple permissions  - calendar permission dicts set each dict
        must contain values for both `calendar_id` and `permission_level`
        :param string redirect_uri - A uri to redirect the end user back to after they
        have either granted or rejected the request for elevated permission.

        In the case of normal accounts:
        After making this call the end user will have to grant the extended
        permissions to their calendar via rhe url returned from the response.

        In the case of service accounts:
        After making this call the exteneded permissions will be granted provided
        the relevant scope has been granted to the account

        :return: a extended permissions response.
        :rtype: ``dict``
        """

        body = {'permissions': permissions}

        if redirect_uri:
            body['redirect_uri'] = redirect_uri

        return self.request_handler.post('permissions', data=body).json()['permissions_request']

    def upsert_smart_invite(self, smart_invite_id, recipient, event, callback_url=None, organizer=None):
        """ Creates or updates smart invite.
        :param string smart_invite_id - A String uniquely identifying the event for your
              application (note: this is NOT an ID generated
              by Cronofy).
        :param string callback_url - The URL within your application you want Cronofy to
             send notifications to about user interactions with
             the Smart Invite.
        :param dict recipient - A Dict containing the intended recipient of the invite
             :email      - A String for the email address you are
                           going to send the Smart Invite to.
        :param dict event - A Dict describing the event with symbolized keys:
             :summary      - A String to use as the summary, sometimes
                             referred to as the name or title, of the
                             event.
             :description  - A String to use as the description, sometimes
                             referred to as the notes or body, of the
                             event.
             :start        - The Time or Date the event starts.
             :end          - The Time or Date the event ends.
             :url          - The URL associated with the event.
             :location     - A Dict describing the location of the event
                             with keys (optional):
                             :description - A String describing the
                                            location.
                             :lat - A String of the location's latitude.
                             :long - A String of the location's longitude.
             :reminders    - An Array of Dicts describing the desired
                             reminders for the event. Reminders should be
                             specified in priority order as, for example,
                             when the underlying provider only supports a
                             single reminder then the first reminder will
                             be used.
                             :minutes - An Integer specifying the number
                                        of minutes before the start of the
                                        event that the reminder should
                                        occur.
             :transparency - The transparency state for the event (optional).
                             Accepted values are "transparent" and "opaque".
             :color        - The color of the event (optional).
        :param dict organizer - A Dict containing the organzier of the invite
             :name      - A String for the name of the organizer.
        """
        event['start'] = format_event_time(event['start'])
        event['end'] = format_event_time(event['end'])

        body = {
            'smart_invite_id': smart_invite_id,
            'event': event
        }
        if type(recipient) == dict:
            body['recipient'] = recipient
        elif type(recipient) == list:
            body['recipients'] = recipient

        if callback_url:
            body['callback_url'] = callback_url

        if organizer:
            body['organizer'] = organizer

        return self.request_handler.post('smart_invites', data=body, use_api_key=True).json()

    def get_smart_invite(self, smart_invite_id, recipient_email):
        """Gets the details for a smart invite.

        :param string smart_invite_id: - A String uniquely identifying the event for your
                                        application (note: this is NOT an ID generated by Cronofy).
        :param string recipient_email: - The email address for the recipient to get details for.
        """
        params = {
            'smart_invite_id': smart_invite_id,
            'recipient_email': recipient_email
        }

        return self.request_handler.get('smart_invites', params=params, use_api_key=True).json()

    def get_authorization_from_code(self, code, redirect_uri=''):
        """Updates the authorization tokens from the user provided code.

        :param string code: Authorization code to pass to Cronofy.
        :param string redirect_uri: Optionally override redirect uri obtained from user_auth_link. (They must match however).
        :return: Dictionary containing auth tokens, expiration info, and response status.
        :rtype: ``dict``
        """
        response = self.request_handler.post(
            url='%s/oauth/token' % settings.API_BASE_URL,
            data={
                'grant_type': 'authorization_code',
                'client_id': self.auth.client_id,
                'client_secret': self.auth.client_secret,
                'code': code,
                'redirect_uri': redirect_uri if redirect_uri else self.auth.redirect_uri,
            })
        data = response.json()
        token_expiration = (datetime.datetime.utcnow() +
                            datetime.timedelta(seconds=data['expires_in']))
        self.auth.update(
            token_expiration=token_expiration,
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
        )
        return {
            'access_token': self.auth.access_token,
            'refresh_token': self.auth.refresh_token,
            'token_expiration': format_event_time(self.auth.token_expiration),
        }

    def application_calendar(self, application_calendar_id):
        """Creates and Retrieves authorization for an application calendar

        :param string application_calendar_id: The Id for this application calendar
        :return: Dictionary containing auth tokens, expiration info, and response status.
        :rtype: ``dict``
        """
        response = self.request_handler.post(
            url='%s/v1/application_calendar' % settings.API_BASE_URL,
            data={
                'client_id': self.auth.client_id,
                'client_secret': self.auth.client_secret,
                'application_calendar_id': application_calendar_id,
            })
        data = response.json()
        token_expiration = (datetime.datetime.utcnow() +
                            datetime.timedelta(seconds=data['expires_in']))
        self.auth.update(
            token_expiration=token_expiration,
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
        )
        return {
            'access_token': self.auth.access_token,
            'refresh_token': self.auth.refresh_token,
            'token_expiration': format_event_time(self.auth.token_expiration),
            'sub': data.get('sub'),
            'application_calendar_id': data.get('application_calendar_id')
        }

    def is_authorization_expired(self):
        """Checks if the authorization token (access_token) has expired.

        :return: If expired.
        :rtype: ``bool``
        """
        if not self.auth.token_expiration:
            return True
        return (datetime.datetime.utcnow() > self.auth.token_expiration)

    def list_calendars(self):
        """Return a list of calendars available for the active account.

        :return: List of calendars (dictionaries).
        :rtype: ``list``
        """
        return self.request_handler.get(endpoint='calendars').json()['calendars']

    def list_profiles(self):
        """Get list of active user's calendar profiles.

        :return: Calendar profiles.
        :rtype: ``list``
        """
        return self.request_handler.get(endpoint='profiles').json()['profiles']

    def list_notification_channels(self):
        """Return a list of notification channels available for the active account.

        :return: List of notification channels (dictionaries).
        :rtype: ``list``
        """
        return self.request_handler.get(endpoint='channels').json()['channels']

    def resources(self):
        """ Lists all the resources for the service account.

        :return: List of Resources (dictionaries).
        :rtype: ``list``
        """
        return self.request_handler.get("resources").json()["resources"]

    def read_events(self,
                    calendar_ids=(),
                    from_date=None,
                    to_date=None,
                    last_modified=None,
                    tzid=settings.DEFAULT_TIMEZONE_ID,
                    only_managed=False,
                    include_managed=True,
                    include_deleted=False,
                    include_moved=False,
                    include_geo=False,
                    localized_times=False,
                    automatic_pagination=True):
        """Read events for linked account (optionally for the specified calendars).

        :param tuple calendar_ids: Tuple or list of calendar ids to pass to cronofy. (Optional).
        :param datetime.date from_date: Start datetime (or ISO8601 string) for query. (Optional).
        :param datetime.date to_date: End datetime (or ISO8601 string) for query. (Optional).
        :param datetime.datetime last_modified: Return items modified on or after last_modified. Datetime or ISO8601 string. (Optional).
        :param string tzid: Timezone ID for query. (Optional, default settings.DEFAULT_TIMEZONE_ID). Should match tzinfo on datetime objects.
        :param bool only_managed: Only include events created through the API. (Optional, default False)
        :param bool include_managed: Include events created through the API. (Optional, default True)
        :param bool include_deleted: Include deleted events. (Optional, default False)
        :param bool include_moved: Include events that ever existed within the from_date/to_date time window. (Optional, default False)
        :param bool include_geo: Include any geo location information for events when available (Optional, default False)
        :param bool localized_times: Return time values for event start/end with localization information. This varies across providers. (Optional, default False).
        :param bool automatic_pagination: Autonatically fetch next page when iterating through results (Optional, default True)
        :return: Wrapped results (Containing first page of events).
        :rtype: ``Pages``
        """
        results = self.request_handler.get(endpoint='events', params={
            'tzid': tzid,
            'calendar_ids[]': calendar_ids,
            'from': format_event_time(from_date),
            'to': format_event_time(to_date),
            'last_modified': format_event_time(last_modified),
            'only_managed': only_managed,
            'include_managed': include_managed,
            'include_deleted': include_deleted,
            'include_moved': include_moved,
            'include_geo': include_geo,
            'localized_times': localized_times,
        }).json()

        return Pages(self.request_handler, results, 'events', automatic_pagination)

    def read_free_busy(self,
                       calendar_ids=(),
                       from_date=None,
                       to_date=None,
                       last_modified=None,
                       tzid=settings.DEFAULT_TIMEZONE_ID,
                       include_managed=True,
                       localized_times=False,
                       automatic_pagination=True):
        """Read free/busy blocks for linked account (optionally for the specified calendars).

        :param tuple calendar_ids: Tuple or list of calendar ids to pass to cronofy. (Optional).
        :param datetime.date from_date: Start datetime (or ISO8601 string) for query. (Optional).
        :param datetime.date to_date: End datetime (or ISO8601 string) for query. (Optional).
        :param string tzid: Timezone ID for query. (Optional, default settings.DEFAULT_TIMEZONE_ID). Should match tzinfo on datetime objects.
        :param bool include_managed: Include pages created through the API. (Optional, default True)
        :param bool localized_times: Return time values for event start/end with localization information. This varies across providers. (Optional, default False).
        :param bool automatic_pagination: Automatically fetch next page when iterating through results (Optional, default True)
        :return: Wrapped results (Containing first page of free/busy blocks).
        :rtype: ``Pages``
        """
        results = self.request_handler.get(endpoint='free_busy', params={
            'tzid': tzid,
            'calendar_ids[]': calendar_ids,
            'from': format_event_time(from_date),
            'to': format_event_time(to_date),
            'include_managed': include_managed,
            'localized_times': localized_times,
        }).json()

        return Pages(self.request_handler, results, 'free_busy', automatic_pagination)

    def availability(self, participants=(), required_duration=(), available_periods=(), start_interval=None, buffer=()):
        """ Performs an availability query.
        :param list participants: An Array of participant groups or a dict for a single participant group.
        :param dict or int required_duration - An Integer representing the minimum number of minutes of availability required.
        :param list available_periods - An Array of available time periods dicts, each must specify a start and end Time.
        :param dict or int start_interval - An Interger representing the start interval minutes for the event.
        :param dict buffer - An Dict representing the buffer to apply to the request.

        :rtype: ``list``
        """
        options = {}
        options['participants'] = self.map_availability_participants(
            participants)
        options['required_duration'] = self.map_availability_required_duration(
            required_duration)
        options['buffer'] = self.map_availability_buffer(buffer)

        if start_interval:
            options['start_interval'] = self.map_availability_required_duration(start_interval)

        self.translate_available_periods(available_periods)
        options['available_periods'] = available_periods

        return self.request_handler.post(endpoint='availability', data=options).json()['available_periods']

    def sequenced_availability(self, sequence=(), available_periods=()):
        """ Performs an availability query.
        :param list sequence: An Array of dics representing sequences to find availability for
                       each sequence can contain.
                :sequence_id - A string identifying this step in the sequence.
                :ordinal - An Integer defining the order of this step in the sequence.
                :participants      - A dict stating who is required for the availability
                                 call
                :required_duration - A dict stating the length of time the event will
                                     last for
                :event - A dict describing the event
                :available_periods - A dict stating the available periods for the step
                :start_interval - An Interger representing the start interval minutes for the event.
                :buffer - An Dict representing the buffer to apply to the request.
        :param list available_periods - An Array of available time periods dicts, each must specify a start and end Time.

        :rtype: ``list``
        """
        options = {}
        options['sequence'] = self.map_availability_sequence(sequence)

        self.translate_available_periods(available_periods)
        options['available_periods'] = available_periods

        return self.request_handler.post(endpoint='sequenced_availability', data=options).json()['sequences']

    def refresh_authorization(self):
        """Refreshes the authorization tokens.

        :return: Dictionary containing auth tokens, expiration info, and response status.
        :rtype: ``dict``
        """
        response = self.request_handler.post(
            url='%s/oauth/token' % settings.API_BASE_URL,
            data={
                'grant_type': 'refresh_token',
                'client_id': self.auth.client_id,
                'client_secret': self.auth.client_secret,
                'refresh_token': self.auth.refresh_token,
            }
        )
        data = response.json()
        token_expiration = (datetime.datetime.utcnow() +
                            datetime.timedelta(seconds=data['expires_in']))
        self.auth.update(
            token_expiration=token_expiration,
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
        )
        return {
            'access_token': self.auth.access_token,
            'refresh_token': self.auth.refresh_token,
            'token_expiration': format_event_time(self.auth.token_expiration),
        }

    def revoke_authorization(self):
        """Revokes Oauth authorization."""
        self.request_handler.post(
            url='%s/oauth/token/revoke' % settings.API_BASE_URL,
            data={
                'client_id': self.auth.client_id,
                'client_secret': self.auth.client_secret,
                'token': self.auth.access_token,
            }
        )
        self.auth.update(
            token_expiration=None,
            access_token=None,
            refresh_token=None,
        )

    def upsert_event(self, calendar_id, event):
        """Inserts or updates an event for the specified calendar.

        :param string calendar_id: ID of calendar to insert/update event into.
        :param dict event: Dictionary of event data to send to cronofy.
        """
        event['start'] = format_event_time(event['start'])
        event['end'] = format_event_time(event['end'])
        self.request_handler.post(
            endpoint='calendars/%s/events' % calendar_id, data=event)

    def authorize_with_service_account(self, email, scope, callback_url, state=None):
        """ Attempts to authorize the email with impersonation from a service account

        :param string email: the email address to impersonate
        :param string callback_url: URL to callback with the OAuth code.
        :param string scope: The scope of the privileges you want the eventual access_token to grant.
        :return: nothing
        """
        params = {
            'email': email,
            'scope': scope,
            'callback_url': callback_url
        }

        if state is not None:
            params['state'] = state

        self.request_handler.post(
            endpoint="service_account_authorizations", data=params)
        None

    def real_time_scheduling(self, availability, oauth, event, target_calendars=()):
        """Generates an real time scheduling link to start the OAuth process with
        an event to be automatically upserted

        :param dict availability:  - A dict describing the availability details for the event:
            :participants      - A dict stating who is required for the availability
                                 call
            :required_duration - A dict stating the length of time the event will
                                 last for
            :available_periods - A dict stating the available periods for the event
            :start_interval    - A Integer representing the start_interval of the event
            :buffer            - A dict representing the buffer for the event
        :param dict oauth:   - A dict describing the OAuth flow required:
            :scope             - A String representing the scopes to ask for
                                 within the OAuth flow
            :redirect_uri      - A String containing a url to redirect the
                                 user to after completing the OAuth flow.
            :scope             - A String representing additional state to
                                 be passed within the OAuth flow.
        :param dict event:     - A dict describing the event
        :param list target_calendars: - An list of dics stating into which calendars
                                        to insert the created event
        See http://www.cronofy.com/developers/api#upsert-event for reference.
        """
        args = {
            'oauth': oauth,
            'event': event,
            'target_calendars': target_calendars
        }

        if availability:
            options = {}
            options['participants'] = self.map_availability_participants(availability.get('participants', None))
            options['required_duration'] = self.map_availability_required_duration(availability.get('required_duration', None))
            options['start_interval'] = self.map_availability_required_duration(availability.get('start_interval', None))
            options['buffer'] = self.map_availability_buffer(availability.get('buffer', None))

            self.translate_available_periods(availability['available_periods'])
            options['available_periods'] = availability['available_periods']
            args['availability'] = options

        return self.request_handler.post(endpoint='real_time_scheduling', data=args, use_api_key=True).json()

    def real_time_sequencing(self, availability, oauth, event, target_calendars=()):
        """Generates an real time sequencing link to start the OAuth process with
        an event to be automatically upserted

        :param dict availability:  - A dict describing the availability details for the event:

            :sequence: An Array of dics representing sequences to find availability for
                       each sequence can contain.
                :sequence_id - A string identifying this step in the sequence.
                :ordinal - An Integer defining the order of this step in the sequence.
                :participants      - A dict stating who is required for the availability
                                 call
                :required_duration - A dict stating the length of time the event will
                                     last for
                :event - A dict describing the event
                :available_periods - A dict stating the available periods for the step
            :available_periods - A dict stating the available periods for the sequence
        :param dict oauth:   - A dict describing the OAuth flow required:
            :scope             - A String representing the scopes to ask for
                                 within the OAuth flow
            :redirect_uri      - A String containing a url to redirect the
                                 user to after completing the OAuth flow.
            :scope             - A String representing additional state to
                                 be passed within the OAuth flow.
        :param dict event:     - A dict describing the event
        :param list target_calendars: - An list of dics stating into which calendars
                                        to insert the created event
        See http://www.cronofy.com/developers/api#upsert-event for reference.
        """
        args = {
            'oauth': oauth,
            'event': event,
            'target_calendars': target_calendars
        }

        if availability:
            options = {}
            options['sequence'] = self.map_availability_sequence(availability.get('sequence', None))

            if availability.get('available_periods', None):
                self.translate_available_periods(availability['available_periods'])
                options['available_periods'] = availability['available_periods']

        args['availability'] = options

        return self.request_handler.post(endpoint='real_time_sequencing', data=args, use_api_key=True).json()

    def user_auth_link(self, redirect_uri, scope='', state='', avoid_linking=False):
        """Generates a URL to send the user for OAuth 2.0

        :param string redirect_uri: URL to redirect the user to after auth.
        :param string scope: The scope of the privileges you want the eventual access_token to grant.
        :param string state: A value that will be returned to you unaltered along with the user's authorization request decision.
        (The OAuth 2.0 RFC recommends using this to prevent cross-site request forgery.)
        :param bool avoid_linking: Avoid linking calendar accounts together under one set of credentials. (Optional, default: false).
        :return: authorization link
        :rtype: ``string``
        """
        if not scope:
            scope = ' '.join(settings.DEFAULT_OAUTH_SCOPE)

        self.auth.update(redirect_uri=redirect_uri)

        url = '%s/oauth/authorize' % self.app_base_url
        params = {
            'response_type': 'code',
            'client_id': self.auth.client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state,
            'avoid_linking': avoid_linking,
        }
        urlencoded_params = urlencode(params)
        return "{url}?{params}".format(url=url, params=urlencoded_params)

    def validate(self, method, *args, **kwargs):
        """Validate authentication and values passed to the specified method.
        Raises a PyCronofyValidationError on error.

        :param string method: Method name to check.
        :param *args: Arguments for "Method".
        :param **kwargs: Keyword arguments for "Method".
        """
        validate(method, self.auth, *args, **kwargs)

    def batch(self, builder):
        requests = builder.build()

        responses = self.request_handler.post(endpoint="batch", data=requests).json().get('batch', [])

        entries = list()
        for (request, response) in zip(requests, responses):
            entries.append(BatchEntry(request, response))

        result = BatchResponse(entries)

        if result.has_errors():
            msg = "Batch contains %i errors" % len(result.errors())
            raise PyCronofyPartialSuccessError(msg, result)

        return result

    def translate_available_periods(self, periods):
        for params in periods:
            for tp in ['start', 'end']:
                if params[tp]:
                    params[tp] = format_event_time(params[tp])

    def map_availability_sequence(self, sequence):
        if isinstance(sequence, collections.Iterable):
            return list(map(lambda item: self.map_sequence_item(item), sequence))
        else:
            return sequence

    def map_availability_buffer(self, buffer):
        result = {}

        if type(buffer) is not dict:
            return result

        if 'before' in buffer:
            result['before'] = self.map_buffer_details(buffer['before'])

        if 'after' in buffer:
            result['after'] = self.map_buffer_details(buffer['after'])

        return result

    def map_buffer_details(self, buffer):
        if type(buffer) is not dict:
            return self.map_availability_required_duration(buffer)

        result = self.map_availability_required_duration(buffer)

        if 'minimum' in buffer:
            result['minimum'] = self.map_availability_required_duration(buffer['minimum'])

        if 'maximum' in buffer:
            result['maximum'] = self.map_availability_required_duration(buffer['maximum'])

        return result

    def map_sequence_item(self, sequence_item):
        sequence_item['participants'] = self.map_availability_participants(sequence_item.get('participants', None))
        sequence_item['required_duration'] = self.map_availability_required_duration(sequence_item.get('required_duration', None))
        sequence_item['start_interval'] = self.map_availability_required_duration(sequence_item.get('start_interval', None))
        sequence_item['buffer'] = self.map_availability_buffer(sequence_item.get('buffer', None))

        if sequence_item.get('available_periods', None):
            self.translate_available_periods(sequence_item['available_periods'])

        return sequence_item

    def map_availability_participants(self, participants):
        if type(participants) is dict:
            # Allow one group to be specified without being nested
            return [self.map_availability_participants_group(participants)]
        elif isinstance(participants, collections.Iterable):
            return list(map(lambda group: self.map_availability_participants_group(group), participants))
        else:
            return participants

    def map_availability_participants_group(self, participants):
        if type(participants) is dict:
            mapped_participants = list(map(lambda member: self.map_availability_member(member), participants.get('members', ())))
            participants['members'] = mapped_participants

            if participants.get('required', None) is None:
                participants['required'] = 'all'

            return participants
        elif isinstance(participants, collections.Iterable):
            return list(map(lambda group: self.map_availability_participants(group), participants))
        else:
            participants

    def map_availability_member(self, member):
        member_type = type(member)

        if member_type in (type(''), type(u'')):
            return {'sub': member}
        elif member_type is dict:
            if member.get('available_periods', None):
                self.translate_available_periods(member['available_periods'])

        return member

    def map_availability_required_duration(self, required_duration):
        if type(required_duration) is int:
            return {'minutes': required_duration}
        else:
            return required_duration
