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

REAL_TIME_SEQUENCING_RESPONSE = {'url': 'http://www.example.com'}


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_real_time_sequencing(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)

        availability = payload['availability']
        assert availability['available_periods'] == [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]

        sequence = availability['sequence'][0]

        assert sequence['sequence_id'] == "1234"
        assert sequence['ordinal'] == 1
        assert sequence['required_duration'] == {'minutes': 30}
        assert sequence['start_interval'] == {'minutes': 30}
        assert sequence['buffer']['before']['minimum'] == {'minutes': 30}
        assert sequence['buffer']['before']['maximum'] == {'minutes': 45}
        assert sequence['buffer']['after']['minimum'] == {'minutes': 45}
        assert sequence['buffer']['after']['maximum'] == {'minutes': 60}
        assert sequence['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002'},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]
        assert sequence['event'] == TEST_EVENT

        second_sequence = availability['sequence'][1]
        assert second_sequence['sequence_id'] == "4567"
        assert second_sequence['ordinal'] == 2

        assert payload['event'] == TEST_EVENT
        assert payload['oauth'] == oauth
        assert payload['minimum_notice'] == {'hours': 4}

        assert request.headers['Authorization'] == "Bearer %s" % client.auth.client_secret

        return (200, {}, json.dumps(REAL_TIME_SEQUENCING_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/real_time_sequencing' % (settings.API_BASE_URL, settings.API_VERSION),
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

    sequence = [
        {
            'sequence_id': "1234",
            'ordinal': 1,
            'participants': example_participants,
            'required_duration': 30,
            'start_interval': 30,
            'buffer': {
                'before': {
                    'minimum': 30,
                    'maximum': 45,
                },
                'after': {
                    'minimum': 45,
                    'maximum': 60,
                },
            },
            'event': TEST_EVENT,
        },
        {
            'sequence_id': "4567",
            'ordinal': 2,
            'participants': example_participants,
            'required_duration': 30,
            'event': TEST_EVENT,
        }
    ]

    availability = {
        'sequence': sequence,
        'available_periods': periods,
    }

    oauth = {
        'scope': 'foo',
        'redirect_uri': 'http://www.example.com',
        'state': 'bar'
    }

    minimum_notice = {
        'hours': 4
    }

    result = client.real_time_sequencing(availability, oauth, TEST_EVENT, [], minimum_notice)
    assert result == REAL_TIME_SEQUENCING_RESPONSE
