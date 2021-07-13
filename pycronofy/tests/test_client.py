import datetime
import json
import pytest
import pytz
import responses
from pycronofy import Client
from pycronofy import settings
from pycronofy.exceptions import PyCronofyRequestError
from pycronofy.tests import common_data


TEST_EVENT = {
    'event_id': 'test-1',
    'summary': 'Test Event',
    'description': 'Talk about how awesome cats are.',
    'start': '2014-10-01T08:00:00Z',
    'end': '2014-10-01T09:00:00Z',
    'tzid': 'Etc/UTC',
    'location': {
        'description': 'Location!',
    },
}

TEST_UPSERT_EVENT_ARGS = {
    'method': responses.POST,
    'url': '%s/%s/calendars/1/events' % (settings.API_BASE_URL, settings.API_VERSION),
    'body': '{"example": 1}',
    'status': 200,
    'content_type': 'application/json'
}

TEST_CALENDAR_NAME = 'test-calendar'

TEST_PROFILE_ID = 'test-profile-id'

TEST_CALENDAR_LIST = [
    {'provider_name': 'live_connect',
     'profile_id': TEST_PROFILE_ID,
     'profile_name': 'testing@live.com',
     'calendar_id': 'testing_cal',
     'calendar_name': TEST_CALENDAR_NAME,
     'calendar_readonly': True,
     'calendar_deleted': True,
     'calendar_primary': False,
     'permission_level': 'unrestricted'},
    {'provider_name': 'google',
     'profile_id': 'test_profile_google',
     'profile_name': 'test-google@gmail.com',
     'calendar_id': 'cal_test_google',
     'calendar_name': TEST_CALENDAR_NAME,
     'calendar_readonly': False,
     'calendar_deleted': False,
     'calendar_primary': False,
     'permission_level': 'unrestricted'}
]


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_change_participation_status(client):
    """Test Client.change_participation_status().

    :param Client client: Client instance with test data.
    """
    calendar_id = "cal_123"
    event_uid = "evt_external_439559854"
    status = "accepted"

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['status'] == status

        return (202, {}, None)

    responses.add_callback(
        responses.POST,
        url='%s/%s/calendars/%s/events/%s/participation_status' % (settings.API_BASE_URL, settings.API_VERSION, calendar_id, event_uid),
        callback=request_callback,
        content_type='application/json',
    )
    result = client.change_participation_status(calendar_id, event_uid, status)
    assert result is None


@responses.activate
def test_delete_event(client):
    """Test Client.delete_event().

    :param Client client: Client instance with test data.
    """
    calendar_id = "cal_123"
    event_id = "example_event_id"

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['event_id'] == event_id

        return (202, {}, None)

    responses.add_callback(
        responses.DELETE,
        url='%s/%s/calendars/%s/events' % (settings.API_BASE_URL, settings.API_VERSION, calendar_id),
        callback=request_callback,
        content_type='application/json',
    )
    result = client.delete_event(calendar_id, event_id)
    assert result is None


@responses.activate
def test_delete_external_event(client):
    """Test Client.delete_external_event().

    :param Client client: Client instance with test data.
    """
    calendar_id = "cal_123"
    event_uid = "evt_external_98343844983"

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['event_uid'] == event_uid

        return (202, {}, None)

    responses.add_callback(
        responses.DELETE,
        url='%s/%s/calendars/%s/events' % (settings.API_BASE_URL, settings.API_VERSION, calendar_id),
        callback=request_callback,
        content_type='application/json',
    )
    result = client.delete_external_event(calendar_id, event_uid)
    assert result is None


@responses.activate
def test_account(client):
    """Test Client.account().

    :param Client client: Client instance with test data.
    """
    responses.add(
        responses.GET,
        url='%s/%s/account' % (settings.API_BASE_URL, settings.API_VERSION),
        body="""{ "account": {
          "account_id": "acc_567236000909002",
          "email": "janed@company.com",
          "name": "Jane Doe",
          "scope": "read_events create_event delete_event",
          "default_tzid": "Europe/London"
        } }
        """,
        status=200,
        content_type='application/json',
    )
    account = client.account()
    assert account['account_id'] == 'acc_567236000909002'
    assert account['email'] == 'janed@company.com'


@responses.activate
def test_userinfo(client):
    """Test Client.userinfo().

    :param Client client: Client instance with test data.
    """
    responses.add(responses.GET,
                  url='%s/%s/userinfo' % (settings.API_BASE_URL, settings.API_VERSION),
                  body='{"sub": "acc_5700a00eb0ccd07000000000", "cronofy.type": "userinfo"}',
                  status=200,
                  content_type='application/json',
                  )
    userinfo = client.userinfo()
    assert userinfo['sub'] == 'acc_5700a00eb0ccd07000000000'
    assert userinfo['cronofy.type'] == 'userinfo'


@responses.activate
def test_create_calendar_with_duplicates_errors(client):
    """Test Client.create_calendar
        - when there is a duplicate calendar error and we want to get the exception,
        ie: the default

    :param Client client: Client instance with test data.
    """
    duplicate_error_json = '{"errors": {"name": [{"key": "errors.duplicate_calendar_name", "description": "A calendar with this name already exists and the provider does not allow duplicates"}]}}'
    responses.add(
        responses.POST,
        url='%s/%s/calendars' % (settings.API_BASE_URL, settings.API_VERSION),
        body=duplicate_error_json,
        status=422,
        content_type='application/json; charset utf-8',
    )
    with pytest.raises(PyCronofyRequestError) as exc_info:
        client.create_calendar(calendar_name=TEST_CALENDAR_NAME, profile_id=TEST_PROFILE_ID)
        assert exc_info.response.json() == duplicate_error_json


@responses.activate
def test_create_calendar_with_duplicate_no_issues(client):
    """Test Client.create_calendar
        - when there is a duplicate calendar error and we dont mind, just use the old one

    :param Client client: Client instance with test data.
    """
    duplicate_error_json = '{"errors": {"name": [{"key": "errors.duplicate_calendar_name", "description": "A calendar with this name already exists and the provider does not allow duplicates"}]}}'
    responses.add(
        responses.POST,
        url='%s/%s/calendars' % (settings.API_BASE_URL, settings.API_VERSION),
        body=duplicate_error_json,
        status=422,
        content_type='application/json; charset utf-8',
    )
    responses.add(
        responses.GET,
        body=json.dumps(dict(calendars=TEST_CALENDAR_LIST)),
        url='%s/%s/calendars' % (settings.API_BASE_URL, settings.API_VERSION),
        status=200,
        content_type='application/json; charset utf-8'
    )
    calendar_data = client.create_calendar(profile_id=TEST_PROFILE_ID, calendar_name=TEST_CALENDAR_NAME, error_on_duplicate=False)
    assert calendar_data
    assert calendar_data['profile_id'] == TEST_PROFILE_ID
    assert calendar_data['calendar_name'] == TEST_CALENDAR_NAME


@responses.activate
def test_create_calendar(client):
    """Test Client.create_calendar

    :param Client client: Client instance with test data.
    """
    responses.add(
        responses.POST,
        url='%s/%s/calendars' % (settings.API_BASE_URL, settings.API_VERSION),
        body="""{"calendar": {"provider_name": "test_provider",
        "profile_id": "%s",
        "profile_name": "my-test-profile-name",
        "calendar_id": "test-calendar-id",
        "calendar_name": "%s",
        "calendar_readonly": false,
        "calendar_deleted": false,
        "calendar_primary": false,
        "permission_level": "unrestricted"}}""" % (TEST_PROFILE_ID, TEST_CALENDAR_NAME),
        status=200,
        content_type='application/json',
    )
    calendar_data = client.create_calendar(profile_id=TEST_PROFILE_ID, calendar_name=TEST_CALENDAR_NAME)
    assert calendar_data['calendar']['profile_id'] == TEST_PROFILE_ID
    assert calendar_data['calendar']['calendar_name'] == TEST_CALENDAR_NAME


@responses.activate
def test_create_notification_channel(client):
    """Test Client.create_notification_channel().

    :param Client client: Client instance with test data.
    """
    responses.add(responses.POST,
                  url='%s/%s/channels' % (settings.API_BASE_URL, settings.API_VERSION),
                  body='{"channel": {"channel_id": "chn_123example", "callback_url": "http://example.com"}}',
                  status=200,
                  content_type='application/json',
                  )
    channel = client.create_notification_channel('http://example.com', calendar_ids=('1',))
    assert channel['channel_id'] == 'chn_123example'


@responses.activate
def test_create_notification_channel_only_managed(client):
    """Test Client.create_notification_channel().

    :param Client client: Client instance with test data.
    """
    responses.add(responses.POST,
                  url='%s/%s/channels' % (settings.API_BASE_URL, settings.API_VERSION),
                  body='{"channel": {"channel_id": "chn_123example", "callback_url": "http://example.com", "filters": {"calendar_ids": ["1"], "only_managed": true}}}',
                  status=200,
                  content_type='application/json',
                  )
    channel = client.create_notification_channel('http://example.com', calendar_ids=('1',), only_managed=True)
    assert channel['filters']['only_managed']


@responses.activate
def test_elevated_permissions(client):
    """Test Client.elevated_permissions().

    :param Client client: Client instance with test data.
    """
    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['redirect_uri'] == 'http://www.example.com'
        assert payload['permissions'] == ({'calendar_id': 'cal_123', 'permission_level': 'unrestricted'})

        body = '{"permissions_request": {"url": "http://app.cronofy.com/permissions/"}}'
        return (200, {}, body)

    responses.add_callback(responses.POST,
                           url='%s/%s/permissions' % (settings.API_BASE_URL, settings.API_VERSION),
                           callback=request_callback,
                           content_type='application/json',
                           )
    permissions = client.elevated_permissions(({'calendar_id': 'cal_123', 'permission_level': 'unrestricted'}), 'http://www.example.com')
    assert permissions['url'] == 'http://app.cronofy.com/permissions/'


@responses.activate
def test_get_authorization_from_code(client):
    """Test update_tokens_from code updates access_token, refresh_token, token_expiration and expires_in.

    :param Client client: Client instance with test data.
    """
    responses.add(responses.POST,
                  '%s/oauth/token' % settings.API_BASE_URL,
                  body='{"access_token": "tail", "refresh_token": "meow", "expires_in": 3600}',
                  status=200,
                  content_type='application/json'
                  )
    authorization = client.get_authorization_from_code('code')
    assert authorization['access_token'] == 'tail'
    assert authorization['refresh_token'] == 'meow'
    assert 'token_expiration' in authorization


@responses.activate
def test_is_authorization_expired(client):
    """Test is_authorization_expired.

    :param Client client: Client instance with test data.
    """
    client.auth.token_expiration = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(seconds=60)
    assert client.is_authorization_expired() is False
    client.auth.token_expiration = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(seconds=60)
    assert client.is_authorization_expired() is True


@responses.activate
def test_refresh(client):
    """Test refresh updates the access_token, expires_in, and token_expiration.

    :param Client client: Client instance with test data.
    """
    responses.add(responses.POST,
                  '%s/oauth/token' % settings.API_BASE_URL,
                  body='{"access_token": "tail", "refresh_token": "wagging", "expires_in": 3600}',
                  status=200,
                  content_type='application/json'
                  )
    old_token_expiration = client.auth.token_expiration
    client.refresh_authorization()
    assert client.auth.access_token == 'tail'
    assert client.auth.token_expiration > old_token_expiration


@responses.activate
def test_revoke(client):
    """Test revoke sets the access_token, refresh_token and token_expiration to None and the expires_in to 0.

    :param Client client: Client instance with test data.
    """
    responses.add(responses.POST,
                  '%s/oauth/token/revoke' % settings.API_BASE_URL,
                  status=200,
                  content_type='application/json'
                  )
    client.revoke_authorization()
    assert client.auth.access_token is None
    assert client.auth.refresh_token is None
    assert client.auth.token_expiration is None


@responses.activate
def test_revoke_profile(client):
    """Test Client.revoke_profile().

    :param Client client: Client instance with test data.
    """
    profile_id = "profile_123"

    responses.add(
        responses.POST,
        url='%s/%s/profiles/%s/revoke' % (settings.API_BASE_URL, settings.API_VERSION, profile_id),
        content_type='application/json',
        status=202
    )
    result = client.revoke_profile(profile_id)
    assert result is None


@responses.activate
def test_upsert_event(client):
    """Test Client.upsert_event().

    :param Client client: Client instance with test data.
    """
    responses.add(**TEST_UPSERT_EVENT_ARGS)
    response = client.upsert_event('1', TEST_EVENT)
    assert response is None


@responses.activate
def test_upsert_event_with_tzid(client):
    """Test Client.upsert_event().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload == test_event

        return (202, {}, None)

    test_event = {
        'event_id': 'test-1',
        'summary': 'Test Event',
        'description': 'Talk about how awesome cats are.',
        'start': {
            'time': '2014-10-01T08:00:00Z',
            'tzid': 'Europe/London'
        },
        'end': {
            'time': '2014-10-01T09:00:00Z',
            'tzid': 'Europe/London'
        },
        'location': {
            'description': 'Location!',
        }
    }

    responses.add_callback(
        responses.POST,
        '%s/%s/calendars/1/events' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    response = client.upsert_event('1', test_event)
    assert response is None


@responses.activate
def test_upsert_smart_invites(client):
    url = "http://www.example.com"
    smart_invite_id = "qTtZdczOccgaPncGJaCiLg"
    recipient = {
        'email': "example@example.com"
    }
    organizer = {
        'name': "Smart invite application"
    }

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['smart_invite_id'] == smart_invite_id
        assert payload['recipient'] == recipient
        assert payload['callback_url'] == url
        assert payload['event'] == TEST_EVENT

        response = {
            "recipient": {
                "email": "cronofy@example.com",
                "status": "pending"
            },
            "smart_invite_id": "your-unique-identifier-for-invite",
            "callback_url": "https://example.yourapp.com/cronofy/smart_invite/notifications",
            "event": {
                "summary": "Board meeting",
                "description": "Discuss plans for the next quarter.",
                "start": "2017-10-05T09:30:00Z",
                "end": "2017-10-05T10:00:00Z",
                "tzid": "Europe/London",
                "location": {
                    "description": "Board room"
                }
            },
            "attachments": {
                "icalendar": "BEGIN:VCALENDAR\nVERSION:2.0..."
            }
        }

        return (202, {}, json.dumps(response))

    responses.add_callback(
        responses.POST,
        '%s/v1/smart_invites' % settings.API_BASE_URL,
        callback=request_callback,
        content_type='application/json',
    )

    result = client.upsert_smart_invite(smart_invite_id, recipient, TEST_EVENT, callback_url=url, organizer=organizer)

    assert result['attachments']['icalendar'] == "BEGIN:VCALENDAR\nVERSION:2.0..."


@responses.activate
def test_upsert_smart_invites_with_multiple_recievers(client):
    url = "http://www.example.com"
    smart_invite_id = "qTtZdczOccgaPncGJaCiLg"
    recipients = [{'email': "example@example.com"}, {'email': "example_2@example.com"}]
    organizer = {
        'name': "Smart invite application"
    }

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['smart_invite_id'] == smart_invite_id
        assert payload['recipients'] == recipients
        assert payload['callback_url'] == url
        assert payload['event'] == TEST_EVENT

        response = {
            "recipients": [
                {
                    "email": "example@example.com",
                    "status": "pending"
                },
                {
                    "email": "example_2@example.com",
                    "status": "pending"
                }
            ],
            "smart_invite_id": "your-unique-identifier-for-invite",
            "callback_url": "https://example.yourapp.com/cronofy/smart_invite/notifications",
            "event": {
                "summary": "Board meeting",
                "description": "Discuss plans for the next quarter.",
                "start": "2017-10-05T09:30:00Z",
                "end": "2017-10-05T10:00:00Z",
                "tzid": "Europe/London",
                "location": {
                    "description": "Board room"
                }
            },
            "attachments": {
                "icalendar": "BEGIN:VCALENDAR\nVERSION:2.0..."
            }
        }

        return (202, {}, json.dumps(response))

    responses.add_callback(
        responses.POST,
        '%s/v1/smart_invites' % settings.API_BASE_URL,
        callback=request_callback,
        content_type='application/json',
    )

    result = client.upsert_smart_invite(smart_invite_id, recipients, TEST_EVENT, callback_url=url, organizer=organizer)

    assert result['attachments']['icalendar'] == "BEGIN:VCALENDAR\nVERSION:2.0..."


@responses.activate
def test_get_smart_invite(client):
    smart_invite_id = "qTtZdczOccgaPncGJaCiLg"
    recipient = "example@example.com"

    def request_callback(request):
        assert request.url == 'https://api.cronofy.com/v1/smart_invites?smart_invite_id=qTtZdczOccgaPncGJaCiLg&recipient_email=example%40example.com'

        response = {
            "recipient": {
                "email": "cronofy@example.com",
                "status": "pending"
            },
            "smart_invite_id": "your-unique-identifier-for-invite",
            "callback_url": "https://example.yourapp.com/cronofy/smart_invite/notifications",
            "event": {
                "summary": "Board meeting",
                "description": "Discuss plans for the next quarter.",
                "start": "2017-10-05T09:30:00Z",
                "end": "2017-10-05T10:00:00Z",
                "tzid": "Europe/London",
                "location": {
                    "description": "Board room"
                }
            },
            "attachments": {
                "icalendar": "BEGIN:VCALENDAR\nVERSION:2.0..."
            }
        }

        return (202, {}, json.dumps(response))

    responses.add_callback(
        responses.GET,
        '%s/v1/smart_invites' % settings.API_BASE_URL,
        callback=request_callback,
        content_type='application/json',
    )

    result = client.get_smart_invite(smart_invite_id, recipient)

    assert result['attachments']['icalendar'] == "BEGIN:VCALENDAR\nVERSION:2.0..."


@responses.activate
def test_cancel_smart_invite(client):
    smart_invite_id = "qTtZdczOccgaPncGJaCiLg"
    recipient = {
        'email': "example@example.com"
    }

    def request_callback(request):
        assert request.url == 'https://api.cronofy.com/v1/smart_invites'

        payload = json.loads(request.body)
        assert payload['method'] == 'cancel'
        assert payload['recipient'] == recipient
        assert payload['smart_invite_id'] == smart_invite_id

        response = {
            "recipient": {
                "email": "example@example.com",
                "status": "pending"
            },
            "smart_invite_id": "qTtZdczOccgaPncGJaCiLg",
            "callback_url": "https://example.yourapp.com/cronofy/smart_invite/notifications",
            "event": {
                "summary": "Board meeting",
                "description": "Discuss plans for the next quarter.",
                "start": "2017-10-05T09:30:00Z",
                "end": "2017-10-05T10:00:00Z",
                "tzid": "Europe/London",
                "location": {
                    "description": "Board room"
                }
            },
            "attachments": {
                "icalendar": "BEGIN:VCALENDAR\nVERSION:2.0..."
            }
        }

        return (202, {}, json.dumps(response))

    responses.add_callback(
        responses.POST,
        '%s/v1/smart_invites' % settings.API_BASE_URL,
        callback=request_callback,
        content_type='application/json',
    )

    result = client.cancel_smart_invite(smart_invite_id, recipient)

    assert result['attachments']['icalendar'] == "BEGIN:VCALENDAR\nVERSION:2.0..."


@responses.activate
def test_cancel_smart_invite_with_multiple_recipients(client):
    smart_invite_id = "qTtZdczOccgaPncGJaCiLg"
    recipients = [
        {
            'email': "example@example.com"
        },
        {
            'email': "cronofy@example.com"
        },
    ]

    def request_callback(request):
        assert request.url == 'https://api.cronofy.com/v1/smart_invites'

        payload = json.loads(request.body)
        assert payload['method'] == 'cancel'
        assert payload['recipients'] == recipients
        assert payload['smart_invite_id'] == smart_invite_id

        response = {
            "recipients": [
                {
                    "email": "example@example.com",
                    "status": "tentative",
                    "comment": "example comment",
                    "proposal": {
                        "start": {
                            "time": "2014-09-13T23:00:00+02:00",
                            "tzid": "Europe/Paris"
                        },
                        "end": {
                            "time": "2014-09-13T23:00:00+02:00",
                            "tzid": "Europe/Paris"
                        }
                    }
                },
                {
                    "email": "cronofy@example.org",
                    "status": "pending"
                }
            ],
            "smart_invite_id": "qTtZdczOccgaPncGJaCiLg",
            "callback_url": "https://example.yourapp.com/cronofy/smart_invite/notifications",
            "event": {
                "summary": "Board meeting",
                "description": "Discuss plans for the next quarter.",
                "start": {
                    "time": "2020-08-07T09:30:00Z",
                    "tzid": "Europe/London"
                },
                "end": {
                    "time": "2020-08-07T10:00:00Z",
                    "tzid": "Europe/London"
                },
                "location": {
                    "description": "Board room"
                }
            },
            "attachments": {
                "icalendar": "BEGIN:VCALENDAR\nVERSION:2.0..."
            }
        }

        return (202, {}, json.dumps(response))

    responses.add_callback(
        responses.POST,
        '%s/v1/smart_invites' % settings.API_BASE_URL,
        callback=request_callback,
        content_type='application/json',
    )

    result = client.cancel_smart_invite(smart_invite_id, recipients)

    assert result['attachments']['icalendar'] == "BEGIN:VCALENDAR\nVERSION:2.0..."


@responses.activate
def test_user_auth_link(client):
    """Test user auth link returns a properly formatted user auth url.

    :param Client client: Client instance with test data.
    """
    url = client.user_auth_link(redirect_uri='http://example.com', scope='felines', state='NY')
    assert 'client_id=%s' % common_data.AUTH_ARGS['client_id'] in url
    url = client.user_auth_link(redirect_uri='http://example.com', state='NY')
    assert settings.APP_BASE_URL in url


@responses.activate
def test_authorize_with_service_account(client):
    """Test authorize_with_service_account with correct dat

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['email'] == "example@example.com"
        assert payload['scope'] == "felines"
        assert payload['state'] == "state example"
        assert payload['callback_url'] == "http://www.example.com/callback"

        return (202, {}, None)

    responses.add_callback(
        responses.POST,
        '%s/v1/service_account_authorizations' % settings.API_BASE_URL,
        callback=request_callback,
        content_type='application/json',
    )
    client.authorize_with_service_account("example@example.com", "felines", "http://www.example.com/callback", state="state example")


@responses.activate
def test_list_resources(client):
    """Test resources listing

    :param Client client: Client instance with test data.
    """
    responses.add(
        responses.GET,
        '%s/v1/resources' % settings.API_BASE_URL,
        body='{"resources":[{"email":"board-room-london@example.com","name":"Board room (London)"},{"email":"3dprinter@example.com","name":"3D Printer"},{"email":"vr-headset@example.com","name":"Oculus Rift"}]}',
        status=200,
        content_type='application/json'
    )
    response = client.resources()

    assert len(response) == 3
    assert response[0]['email'] == "board-room-london@example.com"
    assert response[0]['name'] == "Board room (London)"


@responses.activate
def test_upsert_availability_rule(client):
    """Test Client.upsert_availability_rule().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload == test_availability_rule

        return (200, {}, json.dumps(test_response))

    test_availability_rule = {
        'availability_rule_id': 'rule-1',
        'tzid': 'America/Chicago',
        'calendar_ids': [
            'cal_n23kjnwrw2_jsdfjksn234'
        ],
        'weekly_periods': [
            {
                'day': 'monday',
                'start_time': '09:30',
                'end_time': '12:30'
            },
            {
                'day': 'monday',
                'start_time': '14:00',
                'end_time': '17:00'
            },
            {
                'day': 'wednesday',
                'start_time': '09:30',
                'end_time': '12:30'
            }
        ]
    }

    test_response = {
        'availability_rule': test_availability_rule
    }

    responses.add_callback(
        responses.POST,
        '%s/%s/availability_rules' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    result = client.upsert_availability_rule(test_availability_rule)
    assert result == test_availability_rule


@responses.activate
def test_list_availability_rules(client):
    """Test Client.list_availability_rules().

    :param Client client: Client instance with test data.
    """

    test_availability_rules = [
        {
            'availability_rule_id': 'rule-1',
            'tzid': 'America/Chicago',
            'calendar_ids': [
                'cal_n23kjnwrw2_jsdfjksn234'
            ],
            'weekly_periods': [
                {
                    'day': 'monday',
                    'start_time': '09:30',
                    'end_time': '12:30'
                }
            ]
        },
        {
            'availability_rule_id': 'rule-2',
            'tzid': 'America/Chicago',
            'calendar_ids': [
                'cal_n23kjnwrw2_jsdfjksn234'
            ],
            'weekly_periods': [
                {
                    'day': 'tuesday',
                    'start_time': '13:30',
                    'end_time': '17:30'
                }
            ]
        }
    ]

    test_response = {
        'availability_rules': test_availability_rules
    }

    responses.add(
        responses.GET,
        '%s/%s/availability_rules' % (settings.API_BASE_URL, settings.API_VERSION),
        body=json.dumps(test_response),
        status=200,
        content_type='application/json'
    )

    result = client.list_availability_rules()

    assert result == test_availability_rules


@responses.activate
def test_get_availability_rule(client):
    """Test Client.get_availability_rule().

    :param Client client: Client instance with test data.
    """
    availability_rule_id = 'rule-1'

    test_availability_rule = {
        'availability_rule_id': availability_rule_id,
        'tzid': 'America/Chicago',
        'calendar_ids': [
            'cal_n23kjnwrw2_jsdfjksn234'
        ],
        'weekly_periods': [
            {
                'day': 'monday',
                'start_time': '09:30',
                'end_time': '12:30'
            },
            {
                'day': 'monday',
                'start_time': '14:00',
                'end_time': '17:00'
            },
            {
                'day': 'wednesday',
                'start_time': '09:30',
                'end_time': '12:30'
            }
        ]
    }

    test_response = {
        'availability_rule': test_availability_rule
    }

    responses.add(
        responses.GET,
        '%s/%s/availability_rules/%s' % (settings.API_BASE_URL, settings.API_VERSION, availability_rule_id),
        body=json.dumps(test_response),
        status=200,
        content_type='application/json'
    )

    result = client.get_availability_rule(availability_rule_id)
    assert result == test_availability_rule


@responses.activate
def test_delete_availability_rule(client):
    """Test Client.delete_availability_rule().

    :param Client client: Client instance with test data.
    """
    availability_rule_id = "test-1"

    def request_callback(request):
        return (202, {}, None)

    responses.add_callback(
        responses.DELETE,
        url='%s/%s/availability_rules/%s' % (settings.API_BASE_URL, settings.API_VERSION, availability_rule_id),
        callback=request_callback,
        content_type='application/json',
    )
    result = client.delete_availability_rule(availability_rule_id)
    assert result is None


@responses.activate
def test_hmac_valid(client):
    """Test Client.hmac_valid.

    :param Client client: Client instance with test data.
    """
    assert client.hmac_valid('38ArsN7+J/O8joGsgirVEdV16a/+eb+5QgHGIiuv4hk=', '{\"example\":\"well-known\"}') is True
    assert client.hmac_valid('wrong-hmac', '{\"example\":\"well-known\"}') is False
    assert client.hmac_valid('wrong-hmac,38ArsN7+J/O8joGsgirVEdV16a/+eb+5QgHGIiuv4hk=,wrong-hmac-again', '{\"example\":\"well-known\"}') is True
    assert client.hmac_valid('wrong-hmac,wrong-hmac-again', '{\"example\":\"well-known\"}') is False
    assert client.hmac_valid(None, '{\"example\":\"well-known\"}') is False
    assert client.hmac_valid('', '{\"example\":\"well-known\"}') is False


@responses.activate
def test_get_ui_element_token(client):
    permissions = ["agenda"]
    origin = "http://localhost"
    subs = ["acc_5700a00eb0ccd07000000000"]
    expires_in = 64800

    token = "ELEMENT_TOKEN"

    def request_callback(request):
        payload = json.loads(request.body)

        assert payload["permissions"] == permissions
        assert payload["origin"] == origin
        assert payload["subs"] == subs
        assert payload["version"] == "1"  # as per default

        assert request.headers["Authorization"] == "Bearer %s" % common_data.AUTH_ARGS["client_secret"]

        response_data = {
            "subs": subs,
            "permissions": permissions,
            "token": token,
            "expires_in": expires_in
        }

        return (200, {}, json.dumps(response_data))

    responses.add_callback(
        responses.POST,
        url="%s/%s/element_tokens" % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type="application/json"
    )

    response = client.get_ui_element_token(
        permissions=permissions,
        subs=subs,
        origin=origin
    )

    assert response["token"] == token
    assert response["expires_in"] == expires_in
    assert response["subs"] == subs
    assert response["permissions"] == permissions
