import json
import pytest
import responses
from pycronofy import Client
from pycronofy import settings
from pycronofy.tests import common_data


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_application_calendar(client):
    """Test Client.application_calendar().

    :param Client client: Client instance with test data.
    """

    application_calendar_id = "example-calendar-id"

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['application_calendar_id'] == application_calendar_id
        assert payload['client_id'] == common_data.AUTH_ARGS['client_id']
        assert payload['client_secret'] == common_data.AUTH_ARGS['client_secret']

        body = '{"access_token": "tail", "refresh_token": "meow", "expires_in": 3600}'
        return (200, {}, body)

    responses.add_callback(
        responses.POST,
        url='%s/v1/application_calendar' % (settings.API_BASE_URL),
        callback=request_callback,
        content_type='application/json',
    )
    authorization = client.application_calendar(application_calendar_id)
    assert authorization['access_token'] == 'tail'
    assert authorization['refresh_token'] == 'meow'
    assert 'token_expiration' in authorization
