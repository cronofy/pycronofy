from copy import deepcopy
import pytest
import responses
import requests
from ..client import CronofyClient
from .. import settings
import test_data

@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return CronofyClient(**test_data.AUTH_ARGS)

@responses.activate
def test__get(client):
    """Test CronofyClient.__get().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(method=responses.GET, **test_data.TEST_EVENTS_ARGS)
    response = client._get(endpoint='events')
    assert response['example'] == 1

@responses.activate
def test__post(client):
    """Test CronofyClient.__post().

    :param CronofyClient client: CronofyClient instance with test data.
    """
    responses.add(method=responses.POST, **test_data.TEST_EVENTS_ARGS)
    response = client._post(endpoint='events')
    assert response.status_code == requests.codes.ok