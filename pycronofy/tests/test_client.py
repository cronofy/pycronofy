import datetime
import pytest
import responses
import requests
import json
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
    'content_type':'application/json'
}

@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)

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
    assert result == None

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
    assert result == None

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

        body ='{"permissions_request": {"url": "http://app.cronofy.com/permissions/"}}'
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

def test_is_authorization_expired(client):
    """Test is_authorization_expired.

    :param Client client: Client instance with test data.
    """
    client.auth.token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    assert client.is_authorization_expired() == False
    client.auth.token_expiration = datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
    assert client.is_authorization_expired() == True

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
    response = client.refresh_authorization()
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
    assert client.auth.access_token == None
    assert client.auth.refresh_token == None
    assert client.auth.token_expiration == None

@responses.activate
def test_upsert_event(client):
    """Test Client.upsert_event().

    :param Client client: Client instance with test data.
    """
    responses.add(**TEST_UPSERT_EVENT_ARGS)
    response = client.upsert_event('1', TEST_EVENT)

@responses.activate
def test_user_auth_link(client):
    """Test user auth link returns a properly formatted user auth url.

    :param Client client: Client instance with test data.
    """
    querystring = 'scope=felines&state=NY&redirect_uri=http%%3A%%2F%%2Fexample.com&response_type=code&client_id=%s' % common_data.AUTH_ARGS['client_id']
    auth_url = '%s/oauth/authorize?%s' % (settings.APP_BASE_URL, querystring)
    url = client.user_auth_link(redirect_uri='http://example.com', scope='felines', state='NY')
    assert 'client_id=%s' % common_data.AUTH_ARGS['client_id'] in url
    url = client.user_auth_link(redirect_uri='http://example.com', state='NY')
    assert settings.APP_BASE_URL in url

@responses.activate
def test_authorize_with_service_account(client):
    """Test authorize_with_service_account with correct dat

    :param Client client: Client instance with test data.
    """
    responses.add(responses.POST,
        '%s/v1/service_account_authorizations' % settings.API_BASE_URL,
        status=202,
        content_type='application/json',
    )
    client.authorize_with_service_account("example@example.com", "felines", "http://www.example.com/callback")

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
