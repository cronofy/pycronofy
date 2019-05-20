import pytest
import responses
import json
from pycronofy import Client
from pycronofy import settings
from pycronofy.tests import common_data

TEST_AVAILABLITY_RESPONSE = {
    "available_periods": [
        {
            "start": "2017-01-03T09:00:00Z",
            "end": "2017-01-03T11:00:00Z",
            "participants": [
                {"sub": "acc_567236000909002"},
                {"sub": "acc_678347111010113"}
            ]
        }
    ]
}


TEST_AVAILABLITY_RESPONSE_SLOTS = {
    "available_slots": [
        {
            "start": "2017-01-03T09:00:00Z",
            "end": "2017-01-03T10:00:00Z",
            "participants": [
                {"sub": "acc_567236000909002"},
                {"sub": "acc_678347111010113"}
            ]
        },
        {
            "start": "2017-01-03T10:00:00Z",
            "end": "2017-01-03T11:00:00Z",
            "participants": [
                {"sub": "acc_678347111010113"}
            ]
        }
    ]
}


TEST_SEQUENCED_AVAILABLITY_RESPONSE = {
    "sequences": [
        {
            "sequence": [
                {
                    "sequence_id": "123",
                    "start": "2018-08-18T09:00:00Z",
                    "end": "2018-08-18T10:00:00Z",
                    "participants": [{"sub": "acc_567236000909002"}]
                },
                {
                    "sequence_id": "456",
                    "start": "2018-08-18T10:00:00Z",
                    "end": "2018-08-18T11:00:00Z",
                    "participants": [{"sub": "acc_678347111010113"}]
                }
            ]
        },
        {
            "sequence": [
                {
                    "sequence_id": "123",
                    "start": "2018-08-18T11:00:00Z",
                    "end": "2018-08-18T12:00:00Z",
                    "participants": [{"sub": "acc_567236000909002"}]
                },
                {
                    "sequence_id": "456",
                    "start": "2018-08-18T12:00:00Z",
                    "end": "2018-08-18T13:00:00Z",
                    "participants": [{"sub": "acc_678347111010113"}]
                }
            ]
        }
    ]
}


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_availablity_with_groups(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['required_duration'] == {'minutes': 30}
        assert payload['available_periods'] == [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]
        assert payload['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002'},
                ]
            },
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_678347111010113'},
                ]
            }
        ]

        return (200, {}, json.dumps(TEST_AVAILABLITY_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/availability' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    periods = (
        {'start': "2017-01-03T09:00:00Z", 'end': "2017-01-03T18:00:00Z"},
        {'start': "2017-01-04T09:00:00Z", 'end': "2017-01-04T18:00:00Z"}
    )
    example_participants = (
        {'members': ["acc_567236000909002"]},
        {'members': ["acc_678347111010113"]}
    )

    result = client.availability(required_duration=30, available_periods=periods, participants=example_participants)
    assert len(result) == 1


@responses.activate
def test_availablity_with_simple_values(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['required_duration'] == {'minutes': 30}
        assert payload['start_interval'] == {'minutes': 30}
        assert payload['buffer']['before'] == {'minutes': 30}
        assert payload['buffer']['after'] == {'minutes': 45}
        assert payload['available_periods'] == [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]
        assert payload['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002'},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]

        return (200, {}, json.dumps(TEST_AVAILABLITY_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/availability' % (settings.API_BASE_URL, settings.API_VERSION),
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

    example_buffer = {
        'before': 30,
        'after': {'minutes': 45}
    }

    result = client.availability(required_duration=30, available_periods=periods, participants=example_participants, start_interval=30, buffer=example_buffer)
    assert len(result) == 1


@responses.activate
def test_availablity_with_simple_values_slots_response(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['required_duration'] == {'minutes': 30}
        assert payload['start_interval'] == {'minutes': 30}
        assert payload['buffer']['before'] == {'minutes': 30}
        assert payload['buffer']['after'] == {'minutes': 45}
        assert payload['available_periods'] == [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]
        assert payload['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002'},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]
        assert payload['response_format'] == 'slots'

        return (200, {}, json.dumps(TEST_AVAILABLITY_RESPONSE_SLOTS))

    responses.add_callback(
        responses.POST,
        url='%s/%s/availability' % (settings.API_BASE_URL, settings.API_VERSION),
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

    example_buffer = {
        'before': 30,
        'after': {'minutes': 45}
    }

    example_response_format = 'slots'

    result = client.availability(required_duration=30, available_periods=periods, participants=example_participants, start_interval=30, buffer=example_buffer, response_format=example_response_format)
    assert len(result) == 2


@responses.activate
def test_availablity_with_fully_specified_options(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        expected_periods = [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]

        assert payload['required_duration'] == {'minutes': 30}
        assert payload['buffer']['before']['minimum'] == {'minutes': 30}
        assert payload['buffer']['after']['minimum'] == {'minutes': 45}
        assert payload['available_periods'] == expected_periods
        assert payload['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002', "available_periods": expected_periods},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]
        return (200, {}, json.dumps(TEST_AVAILABLITY_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/availability' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    periods = (
        {'start': "2017-01-03T09:00:00Z", 'end': "2017-01-03T18:00:00Z"},
        {'start': "2017-01-04T09:00:00Z", 'end': "2017-01-04T18:00:00Z"}
    )
    example_participants = ({
        'members': [
            {'sub': "acc_567236000909002", "available_periods": periods},
            {'sub': "acc_678347111010113"},
        ],
        'required': 'all'
    })

    example_buffer = {
        'before': {
            'minimum': {'minutes': 30}
        },
        'after': {
            'minimum': 45
        }
    }

    result = client.availability(required_duration={'minutes': 30}, available_periods=periods, participants=example_participants, buffer=example_buffer)
    assert(len(result)) == 1


@responses.activate
def test_sequenced_availablity_with_simple_values(client):
    """Test Client.availability().

    :param Client client: Client instance with test data.
    """

    def request_callback(request):
        payload = json.loads(request.body)
        assert payload['available_periods'] == [
            {'start': '2017-01-03T09:00:00Z', 'end': '2017-01-03T18:00:00Z'},
            {'start': '2017-01-04T09:00:00Z', 'end': '2017-01-04T18:00:00Z'}
        ]

        first_sequence = payload['sequence'][0]
        assert first_sequence['participants'] == [
            {
                'required': 'all',
                'members': [
                    {'sub': 'acc_567236000909002'},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]
        assert first_sequence['sequence_id'] == "1234"
        assert first_sequence['ordinal'] == 1
        assert first_sequence['required_duration'] == {'minutes': 30}
        assert first_sequence['start_interval'] == {'minutes': 60}
        assert first_sequence['buffer']['before']['minimum'] == {'minutes': 30}
        assert first_sequence['buffer']['before']['maximum'] == {'minutes': 45}
        assert first_sequence['buffer']['after']['minimum'] == {'minutes': 45}
        assert first_sequence['buffer']['after']['maximum'] == {'minutes': 60}

        second_sequence = payload['sequence'][1]
        assert second_sequence['sequence_id'] == "4567"
        assert second_sequence['ordinal'] == 2

        return (200, {}, json.dumps(TEST_SEQUENCED_AVAILABLITY_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/sequenced_availability' % (settings.API_BASE_URL, settings.API_VERSION),
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

    example_buffer = {
        'before': {
            'minimum': 30,
            'maximum': 45
        },
        'after': {
            'minimum': 45,
            'maximum': 60
        }
    }

    sequence = [
        {
            'sequence_id': "1234",
            'ordinal': 1,
            'participants': example_participants,
            'required_duration': 30,
            'start_interval': 60,
            'buffer': example_buffer,
        },
        {
            'sequence_id': "4567",
            'ordinal': 2,
            'participants': example_participants,
            'required_duration': 30,
        }
    ]

    result = client.sequenced_availability(sequence=sequence, available_periods=periods)
    assert len(result) == 2
