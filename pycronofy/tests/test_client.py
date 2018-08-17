import datetime
import json
import pytest
import responses
from pycronofy import Client
from pycronofy import settings
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
    client.auth.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    assert client.is_authorization_expired() is False
    client.auth.token_expiration = datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
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
    responses.add(responses.GET,
                  '%s/v1/resources' % settings.API_BASE_URL,
                  body='{"resources":[{"email":"board-room-london@example.com","name":"Board room (London)"},{"email":"3dprinter@example.com","name":"3D Printer"},{"email":"vr-headset@example.com","name":"Oculus Rift"}]}',
                  status=200,
                  content_type='application/json'
                  )
    response = client.resources()

    assert len(response) == 3
    assert response[0]['email'] == "board-room-london@example.com"
    assert response[0]['name'] == "Board room (London)"
