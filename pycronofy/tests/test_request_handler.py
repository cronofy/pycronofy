import pytest
import requests
import responses
from pycronofy.client import CronofyClient
from pycronofy import settings
import common_data

TEST_EVENTS_ARGS = { 
    'url': '%s/%s/events' % (settings.API_BASE_URL, settings.API_VERSION),
    'body': '{"example": 1}',
    'status': 200,
    'content_type':'application/json'
}

@pytest.fixture(scope="module")
def request_handler():
    """Setup RequestHandler instance with test values."""
    return CronofyClient(**common_data.AUTH_ARGS).request_handler

@responses.activate
def test_get(request_handler):
    """Test RequestHandler.get().

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    responses.add(method=responses.GET, **TEST_EVENTS_ARGS)
    response = request_handler.get(endpoint='events')
    assert response['example'] == 1

@responses.activate
def test_post(request_handler):
    """Test RequestHandler.post().

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    responses.add(method=responses.POST, **TEST_EVENTS_ARGS)
    response = request_handler.post(endpoint='events')
    assert response.status_code == requests.codes.ok