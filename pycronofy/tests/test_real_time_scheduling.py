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

REAL_TIME_SCHEDULING_RESPONSE = {
    'real_time_scheduling': {
        'real_time_scheduling_id': "sch_4353945880944395",
        'url': 'https://app.cronofy.com/rts/example'
    }
}


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
        assert payload['minimum_notice'] == {'hours': 4}

        assert payload['callback_url'] == 'http://www.example.com/callback'
        assert payload['redirect_urls']['completed_url'] == 'http://www.example.com/completed'

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

    minimum_notice = {
        'hours': 4
    }

    callback_url = 'http://www.example.com/callback'

    redirect_urls = {
        'completed_url': 'http://www.example.com/completed'
    }

    result = client.real_time_scheduling(availability, oauth, TEST_EVENT, [], minimum_notice, callback_url=callback_url, redirect_urls=redirect_urls)
    assert result == REAL_TIME_SCHEDULING_RESPONSE


@responses.activate
def test_real_time_scheduling_with_target_calendars(client):
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
                'required': 1,
                'members': [
                    {'sub': 'acc_567236000909002'},
                    {'sub': 'acc_678347111010113'}
                ]
            }
        ]

        assert payload['target_calendars'] == [
            {
                'sub': "acc_567236000909002",
                'calendar_id': "cal_ABCDEF2ubSrL4a7x_aBCDE@f7mZzc2ufdgAciZvA",
                'event': {
                    'conferencing': {
                        'profile_id': "integrated"
                    }
                },
                'attendee': {
                    'email': "support@cronofy.com",
                    'display_name': "Marty McFly"
                }
            },
            {
                'sub': "acc_678347111010113",
                'calendar_id': "cal_HIJKLM2ubSrL0a2e_lFGHI@f5mZzc6ufdgBciYvZ",
                'event': {
                    'conferencing': {
                        'profile_id': "pro_ZYwjVpYOFWgx6eYl"
                    }
                },
                'attendee': {
                    'email': "support@cronofy.com",
                    'display_name': "Doc Brown"
                }
            }
        ]

        assert payload['event'] == TEST_EVENT
        assert payload['oauth'] == oauth
        assert payload['minimum_notice'] == {'hours': 4}

        assert payload['callback_url'] == 'http://www.example.com/callback'
        assert payload['redirect_urls']['completed_url'] == 'http://www.example.com/completed'

        assert payload['event_creation'] == "single"

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
        'required': 1
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

    target_calendars = (
        {
            'sub': "acc_567236000909002",
            'calendar_id': "cal_ABCDEF2ubSrL4a7x_aBCDE@f7mZzc2ufdgAciZvA",
            'event': {
                'conferencing': {
                    'profile_id': "integrated"
                }
            },
            'attendee': {
                'email': "support@cronofy.com",
                'display_name': "Marty McFly"
            }
        },
        {
            'sub': "acc_678347111010113",
            'calendar_id': "cal_HIJKLM2ubSrL0a2e_lFGHI@f5mZzc6ufdgBciYvZ",
            'event': {
                'conferencing': {
                    'profile_id': "pro_ZYwjVpYOFWgx6eYl"
                }
            },
            'attendee': {
                'email': "support@cronofy.com",
                'display_name': "Doc Brown"
            }
        }
    )

    minimum_notice = {
        'hours': 4
    }

    callback_url = 'http://www.example.com/callback'

    redirect_urls = {
        'completed_url': 'http://www.example.com/completed'
    }

    event_creation = "single"

    result = client.real_time_scheduling(availability, oauth, TEST_EVENT, target_calendars, minimum_notice, callback_url=callback_url, redirect_urls=redirect_urls, event_creation=event_creation)
    assert result == REAL_TIME_SCHEDULING_RESPONSE


@responses.activate
def test_real_time_scheduling_when_callback_urls_is_dictionary(client):
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
        assert payload['minimum_notice'] == {'hours': 4}

        assert payload['callback_urls']['completed_url'] == 'http://www.example.com/completed_callback'
        assert payload['callback_urls']['no_times_suitable_url'] == 'http://www.example.com/no_times_suitable_url_callback'
        assert payload['callback_urls']['no_times_displayed_url'] == 'http://www.example.com/no_times_displayed_url_callback'

        assert payload['redirect_urls']['completed_url'] == 'http://www.example.com/completed'

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

    minimum_notice = {
        'hours': 4
    }

    callback_urls = {
        'completed_url': 'http://www.example.com/completed_callback',
        'no_times_suitable_url': 'http://www.example.com/no_times_suitable_url_callback',
        'no_times_displayed_url': 'http://www.example.com/no_times_displayed_url_callback'
    }

    redirect_urls = {
        'completed_url': 'http://www.example.com/completed'
    }

    result = client.real_time_scheduling(availability, oauth, TEST_EVENT, [], minimum_notice, callback_urls=callback_urls, redirect_urls=redirect_urls)
    assert result == REAL_TIME_SCHEDULING_RESPONSE


@responses.activate
def test_get_real_time_scheduling_status_by_token(client):

    def request_callback(request):
        assert request.headers['Authorization'] == "Bearer %s" % client.auth.client_secret
        return (200, {}, json.dumps(REAL_TIME_SCHEDULING_RESPONSE))

    responses.add_callback(
        responses.GET,
        url='%s/%s/real_time_scheduling?token=example' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
        match_querystring=True,
    )

    result = client.get_real_time_scheduling_status(token='example')
    assert result == REAL_TIME_SCHEDULING_RESPONSE


@responses.activate
def test_get_real_time_scheduling_status_by_id(client):

    def request_callback(request):
        assert request.headers['Authorization'] == "Bearer %s" % client.auth.client_secret
        return (200, {}, json.dumps(REAL_TIME_SCHEDULING_RESPONSE))

    responses.add_callback(
        responses.GET,
        url='%s/%s/real_time_scheduling/sch_4353945880944395' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    result = client.get_real_time_scheduling_status(real_time_scheduling_id='sch_4353945880944395')
    assert result == REAL_TIME_SCHEDULING_RESPONSE


@responses.activate
def test_disable_real_time_scheduling_link(client):
    def request_callback(request):
        payload = json.loads(request.body)

        assert request.headers['Authorization'] == "Bearer %s" % client.auth.client_secret
        assert payload['display_message'] == 'test message'

        return (200, {}, json.dumps(REAL_TIME_SCHEDULING_RESPONSE))

    responses.add_callback(
        responses.POST,
        url='%s/%s/real_time_scheduling/%s/disable' % (settings.API_BASE_URL, settings.API_VERSION, 'sch_4353945880944395'),
        callback=request_callback,
        content_type='application/json',
    )

    result = client.disable_real_time_scheduling_link('sch_4353945880944395', 'test message')
    assert result == REAL_TIME_SCHEDULING_RESPONSE
