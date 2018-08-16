import pytest
import responses
import json
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

REAL_TIME_SCHEDULING_RESPONSE = {'url': 'http://www.example.com'}


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_real_time_scheduling(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)

        availability = payload['availability']
        assert availability['required_duration'] == {'minutes': 30}
        assert availability['start_interval'] == {'minutes': 30}
        assert availability['buffer']['before'] == {'minutes': 30}
        assert availability['buffer']['after'] == {'minutes': 45}
        assert availability['available_periods'] == [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]
        assert availability['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002'},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]

        assert payload['event'] == TEST_EVENT
        assert payload['oauth'] == oauth
        assert request.headers['Authorization'] == "Bearer %s" % client.auth.client_secret

        return (200, {}, json.dumps(REAL_TIME_SCHEDULING_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/real_time_scheduling' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    periods = (
        {'start': "2017-01-03T09:00:00Z", 'end': "2017-01-03T18:00:00Z"},
        {'start': "2017-01-04T09:00:00Z", 'end': "2017-01-04T18:00:00Z"}
    )
    example_participants = ({
        'members': [
            "acc_567236000909002",
            "acc_678347111010113",
        ],
    })

    availability = {
        'participants': example_participants,
        'available_periods': periods,
        'required_duration': 30,
        'start_interval': 30,
        'buffer': {
            'before': 30,
            'after': 45,
        },
    }

    oauth = {
        'scope': 'foo',
        'redirect_uri': 'http://www.example.com',
        'state': 'bar'
    }

    result = client.real_time_scheduling(availability, oauth, TEST_EVENT)
    assert result == REAL_TIME_SCHEDULING_RESPONSE
