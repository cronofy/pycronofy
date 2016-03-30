import datetime
import pytest
import responses
import requests
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
    responses.add(responses.GET,
        '%s/oauth/authorize' % settings.APP_BASE_URL,
        status=200,
        body='{"url": "%s"}' % auth_url,
        content_type='application/json'
    )
    url = client.user_auth_link(redirect_uri='http://example.com', scope='felines', state='NY')
    assert 'client_id=%s' % common_data.AUTH_ARGS['client_id'] in url
    url = client.user_auth_link(redirect_uri='http://example.com', state='NY')
    assert settings.APP_BASE_URL in url
