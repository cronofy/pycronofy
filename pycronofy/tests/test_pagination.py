from copy import deepcopy
import json
import pytest
import responses
from pycronofy import Client
from pycronofy.pagination import Pages
from pycronofy import settings
from pycronofy.tests import common_data

TEST_DATA_PAGE_ONE = {
    "pages": {
        "current": 1,
        "total": 2,
        "next_page": "%s/%s/events/pages/08a07b034306679e" % (settings.API_BASE_URL, settings.API_VERSION)
    },
    "events": [
        {
            "calendar_id": "cal_U9uuErStTG@EAAAB_IsAsykA2DBTWqQTf-f0kJw",
            "event_uid": "evt_external_54008b1a4a41730f8d5c6037",
            "summary": "Company Retreat",
            "description": "",
            "start": "2014-09-06",
            "end": "2014-09-08",
            "deleted": False,
            "location": {
                "description": "Beach"
            },
            "participation_status": "needs_action",
            "transparency": "opaque",
            "event_status": "confirmed",
            "categories": [],
            "attendees": [
                {
                    "email": "example@cronofy.com",
                    "display_name": "Example Person",
                    "status": "needs_action"
                }
            ],
            "created": "2014-09-01T08:00:01Z",
            "updated": "2014-09-01T09:24:16Z"
        }
    ]
}

TEST_DATA_PAGE_TWO = {
    "pages": {
        "current": 2,
        "total": 2,
        "next_page": ""
    },
    "events": [
        {
            "calendar_id": "cal_U9uuErStTG@EAAAB_IsAsykA2DBTWqQTf-f0kJw",
            "event_uid": "evt_external_64008b1a4a41730f8d5c6057",
            "summary": "Company Retreat 2",
            "description": "",
            "start": "2014-10-06",
            "end": "2014-10-08",
            "deleted": False,
            "location": {
                "description": "Mountains"
            },
            "participation_status": "needs_action",
            "transparency": "opaque",
            "event_status": "confirmed",
            "categories": [],
            "attendees": [
                {
                    "email": "example@cronofy.com",
                    "display_name": "Example Person",
                    "status": "needs_action"
                }
            ],
            "created": "2014-10-01T08:00:01Z",
            "updated": "2014-10-01T09:24:16Z"
        }
    ]
}

NEXT_PAGE_GET_ARGS = {
    'method': responses.GET,
    'url': '%s/%s/events/pages/08a07b034306679e' % (settings.API_BASE_URL, settings.API_VERSION),
    'body': json.dumps(TEST_DATA_PAGE_TWO),
    'status': 200,
    'content_type': 'application/json'
}


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_all(client):
    """Test Pages.all() returns all pages.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    responses.add(**NEXT_PAGE_GET_ARGS)
    results = pages.all()
    assert len(results) == 2
    assert results[0]['summary'] == TEST_DATA_PAGE_ONE['events'][0]['summary']
    assert results[1]['summary'] == TEST_DATA_PAGE_TWO['events'][0]['summary']


def test_current_page(client):
    """Test Pages.current_page() returns current page.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    assert pages.current_page() == TEST_DATA_PAGE_ONE['events']


@responses.activate
def test_fetch_next_page(client):
    """Test Pages.fetch_next_page() fetches next page.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    responses.add(**NEXT_PAGE_GET_ARGS)
    pages.fetch_next_page()
    assert pages[0]['summary'] == TEST_DATA_PAGE_TWO['events'][0]['summary']


def test_json(client):
    """Test Pages.json() returns raw json for page one.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    assert pages.json() == TEST_DATA_PAGE_ONE


@responses.activate
def test_next(client):
    """Test Pages iterator iterates through all pages.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    responses.add(**NEXT_PAGE_GET_ARGS)
    results = []
    for item in pages:
        results.append(item)
    assert len(results) == 2
    assert results[0]['summary'] == TEST_DATA_PAGE_ONE['events'][0]['summary']
    assert results[1]['summary'] == TEST_DATA_PAGE_TWO['events'][0]['summary']


def test___getitem__(client):
    """Test Pages.__getitem__() returns the item at the specified index.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    assert pages[0]['summary'] == TEST_DATA_PAGE_ONE['events'][0]['summary']


def test___len__(client):
    """Test Pages.__len__() returns the length of the current page of data.

    :param Client client: Client instance with test data.
    """
    pages = Pages(request_handler=client.request_handler, data=deepcopy(TEST_DATA_PAGE_ONE), data_type='events')
    assert len(pages) == 1
