import pytest
import responses
import requests
from pycronofy.client import CronofyClient
from pycronofy import settings
import common_data

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

TEST_CREATE_NOTIFICATION_ARGS = { 
    'method': responses.POST,
    'url': '%s/%s/channels' % (settings.API_BASE_URL, settings.API_VERSION),
    'body': '{"example": 1}',
    'status': 200,
    'content_type':'application/json'
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
    return CronofyClient(**common_data.AUTH_ARGS)

@responses.activate
def test_create_notification_channel(client):
    """Test CronofyClient.create_notification_channel().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(**TEST_CREATE_NOTIFICATION_ARGS)
    response = client.create_notification_channel('http://example.com', calendar_ids=('1',))
    assert response.status_code == requests.codes.ok

@responses.activate
def test_get_authorization_from_code(client):
    """Test update_tokens_from code updates access_token, refresh_token, authorization_datetime and expires_in.

    :param Auth auth: Auth instance with test data.
    """
    responses.add(responses.POST, 
        '%s/oauth/token' % settings.API_BASE_URL,
        body='{"access_token": "tail", "refresh_token": "meow", "expires_in": 3600}', 
        status=200,
        content_type='application/json'
    )
    response = client.get_authorization_from_code('code')
    assert client.auth.access_token == 'tail'
    assert client.auth.refresh_token == 'meow'
    assert client.auth.expires_in == 3600

@responses.activate
def test_refresh(client):
    """Test refresh updates the access_token, expires_in, and authorization_datetime.

    :param Auth auth: Auth instance with test data.
    """
    responses.add(responses.POST, 
        '%s/oauth/token' % settings.API_BASE_URL,
        body='{"access_token": "tail", "expires_in": 3600}', 
        status=200,
        content_type='application/json'
    )
    old_auth_datetime = client.auth.authorization_datetime
    response = client.refresh_access_token()
    assert response.status_code == requests.codes.ok
    assert client.auth.access_token == 'tail'
    assert client.auth.expires_in == 3600
    assert client.auth.authorization_datetime > old_auth_datetime

@responses.activate
def test_revoke(client):
    """Test revoke sets the access_token, refresh_token and authorization_datetime to None and the expires_in to 0.

    :param Auth auth: Auth instance with test data.
    """
    responses.add(responses.POST, 
        '%s/oauth/token/revoke' % settings.API_BASE_URL,
        status=200,
        content_type='application/json'
    )
    response = client.revoke_authorization()
    assert response.status_code == requests.codes.ok
    assert client.auth.access_token == None
    assert client.auth.refresh_token == None
    assert client.auth.expires_in == 0
    assert client.auth.authorization_datetime == None

@responses.activate
def test_upsert_event(client):
    """Test CronofyClient.upsert_event().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(**TEST_UPSERT_EVENT_ARGS)
    response = client.upsert_event('1', TEST_EVENT)
    assert response.status_code == requests.codes.ok
    with pytest.raises(Exception) as exception_info:
        response = client.upsert_event('1', {})
    assert 'not found in event' in exception_info.value.message

@responses.activate
def test_user_auth_link(client):
    """Test user auth link returns a properly formatted user auth url.

    :param Auth auth: Auth instance with test data.
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
    assert url == auth_url
    url = client.user_auth_link(redirect_uri='http://example.com', state='NY')
    assert settings.APP_BASE_URL in url
