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

TEST_EVENTS_ARGS = { 
    'url': '%s/%s/events' % (settings.API_BASE_URL, settings.API_VERSION),
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
def test_upsert_event(client):
    """Test CronofyClient.upsert_event().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(**TEST_UPSERT_EVENT_ARGS)
    response = client.upsert_event('1', TEST_EVENT)
    assert response.status_code == requests.codes.ok

@responses.activate
def test__get(client):
    """Test CronofyClient._get().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(method=responses.GET, **TEST_EVENTS_ARGS)
    response = client._get(endpoint='events')
    assert response['example'] == 1

@responses.activate
def test__post(client):
    """Test CronofyClient._post().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(method=responses.POST, **TEST_EVENTS_ARGS)
    response = client._post(endpoint='events')
    assert response.status_code == requests.codes.ok