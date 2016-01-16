import pytest
import responses
import requests
from ..client import CronofyClient
from ..pagination import Pages
from .. import settings
import test_data

@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return CronofyClient(**test_data.AUTH_ARGS)

@responses.activate
def test_all(client):
    """Test Pages.all() returns all pages.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    responses.add(**test_data.NEXT_PAGE_GET_ARGS)
    results = pages.all()
    assert len(results) == 2
    assert results[0]['summary'] == test_data.TEST_DATA_PAGE_ONE['events'][0]['summary']
    assert results[1]['summary'] == test_data.TEST_DATA_PAGE_TWO['events'][0]['summary']

def test_current_page(client):
    """Test Pages.current_page() returns current page.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    assert pages.current_page() == test_data.TEST_DATA_PAGE_ONE['events']

@responses.activate
def test_fetch_next_page(client):
    """Test Pages.fetch_next_page() fetches next page.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    responses.add(**test_data.NEXT_PAGE_GET_ARGS)
    pages.fetch_next_page()
    assert pages[0]['summary'] == test_data.TEST_DATA_PAGE_TWO['events'][0]['summary']

def test_json(client):
    """Test Pages.json() returns raw json for page one.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    assert pages.json() == test_data.TEST_DATA_PAGE_ONE

@responses.activate
def test_next(client):
    """Test Pages iterator iterates through all pages.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    responses.add(**test_data.NEXT_PAGE_GET_ARGS)
    results = []
    for item in pages:
        results.append(item)
    assert len(results) == 2
    assert results[0]['summary'] == test_data.TEST_DATA_PAGE_ONE, data_type='events')
    assert results[1]['summary'] == test_data.TEST_DATA_PAGE_TWO['events'][0]['summary']

def test___getitem__(client):
    """Test Pages.__getitem__() returns the item at the specified index.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    assert pages[0]['summary'] == test_data.TEST_DATA_PAGE_ONE, data_type='events')

def test___len__(client):
    """Test Pages.__len__() returns the length of the current page of data.

    :param CronofyClient client: CronofyClient instance with test data.
    """
    pages = Pages(client=client, data=test_data.TEST_DATA_PAGE_ONE, data_type='events')
    assert len(pages) == 1
