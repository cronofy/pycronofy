from copy import deepcopy
import pytest
import requests
import responses
import pycronofy
from pycronofy import Client, settings
from pycronofy.tests import common_data

TEST_EVENTS_ARGS = {
    'url': '%s/%s/events' % (settings.API_BASE_URL, settings.API_VERSION),
    'body': '{"example": 1}',
    'status': 200,
    'content_type': 'application/json'
}


@pytest.fixture(scope="module")
def request_handler():
    """Setup RequestHandler instance with test values."""
    return Client(**common_data.AUTH_ARGS).request_handler


@responses.activate
def test_accepted(request_handler):
    """Test RequestHandler.get() handles an accepted status.

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    args = deepcopy(TEST_EVENTS_ARGS)
    args['status'] = 202
    responses.add(method=responses.GET, **args)
    response = request_handler.get(endpoint='events')
    assert response.status_code == requests.codes.accepted
    assert response.json()['example'] == 1


@responses.activate
def test_get(request_handler):
    """Test RequestHandler.get().

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    responses.add(method=responses.GET, **TEST_EVENTS_ARGS)
    response = request_handler.get(endpoint='events')
    assert response.status_code == requests.codes.ok
    assert response.json()['example'] == 1


@responses.activate
def test_delete(request_handler):
    """Test RequestHandler.delete().

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    calendar_id = '123'
    event_id = 'evt_12345'
    responses.add(
        method=responses.DELETE,
        url='%s/%s/calendars/%s/events' % (settings.API_BASE_URL, settings.API_VERSION, calendar_id),
        status=200,
        content_type='application/json',
    )
    response = request_handler.delete(endpoint='calendars/%s/events' % calendar_id, params={'event_id': event_id})
    assert response.status_code == requests.codes.ok


@responses.activate
def test_headers(request_handler):
    """Test headers sent using RequestHandler._request().

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    responses.add(method=responses.POST, **TEST_EVENTS_ARGS)
    response = request_handler._request('post', url=TEST_EVENTS_ARGS['url'])
    assert ('Authorization' in response.request.headers)
    assert ('User-Agent' in response.request.headers)
    assert response.request.headers['Authorization'] == 'Bearer %s' % common_data.AUTH_ARGS['access_token']
    assert response.request.headers['User-Agent'] == '%s %s' % (pycronofy.__name__, pycronofy.__version__)


@responses.activate
def test_post(request_handler):
    """Test RequestHandler.post().

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    responses.add(method=responses.POST, **TEST_EVENTS_ARGS)
    response = request_handler.post(endpoint='events')
    assert response.status_code == requests.codes.ok


@responses.activate
def test_unauthorized(request_handler):
    """Test RequestHandler.get() handles an accepted status.

    :param RequestHandler request_handler: RequestHandler instance with test data.
    """
    args = deepcopy(TEST_EVENTS_ARGS)
    args['status'] = 403
    responses.add(method=responses.GET, **args)
    with pytest.raises(Exception) as exception_info:
        request_handler.get(endpoint='events')
    assert exception_info.typename == 'PyCronofyRequestError'
