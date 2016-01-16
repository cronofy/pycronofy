import json
import pytest
import responses
import requests
from ..client import CronofyClient
from ..pagination import Pages
from .. import settings

TEST_DATA_PAGE_ONE = {
  "pages": {
    "current": 1,
    "total": 2,
    "next_page": "https://api.cronofy.com/v1/events/pages/08a07b034306679e"
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
    'url': 'https://api.cronofy.com/v1/events/pages/08a07b034306679e',
    'body': json.dumps(TEST_DATA_PAGE_TWO),
    'status': 200,
    'content_type':'application/json'
}

@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return CronofyClient(client_id='cats', client_secret='opposable thumbs', access_token='paw', refresh_token='teeth')

@responses.activate
def test_all(client):
    """Test Pages.all() returns all pages.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    responses.add(**NEXT_PAGE_GET_ARGS)
    results = pages.all()
    assert len(results) == 2
    assert results[0]['summary'] == 'Company Retreat'
    assert results[1]['summary'] == 'Company Retreat 2'

def test_current_page(client):
    """Test Pages.current_page() returns current page.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    assert pages.current_page() == TEST_DATA_PAGE_ONE['events']

@responses.activate
def test_fetch_next_page(client):
    """Test Pages.fetch_next_page() fetches next page.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    responses.add(**NEXT_PAGE_GET_ARGS)
    pages.fetch_next_page()
    assert pages[0]['summary'] == 'Company Retreat 2'

def test_json(client):
    """Test Pages.json() returns raw json for page one.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    assert pages.json() == TEST_DATA_PAGE_ONE

@responses.activate
def test_next(client):
    """Test Pages iterator iterates through all pages.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    responses.add(**NEXT_PAGE_GET_ARGS)
    results = []
    for item in pages:
        results.append(item)
    assert len(results) == 2
    assert results[0]['summary'] == 'Company Retreat'
    assert results[1]['summary'] == 'Company Retreat 2'

def test___getitem__(client):
    """Test Pages.__getitem__() returns the item at the specified index.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    assert pages[0]['summary'] == 'Company Retreat'

def test___len__(client):
    """Test Pages.__len__() returns the length of the current page of data.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=TEST_DATA_PAGE_ONE, data_type='events')
    assert len(pages) == 1
