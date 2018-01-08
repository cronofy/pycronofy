import pytest
import responses
import json
from pycronofy import Client
from pycronofy import settings
from pycronofy.tests import common_data
from pycronofy.batch import BatchBuilder
from pycronofy.exceptions import PyCronofyPartialSuccessError


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_batch(client):
    builder = BatchBuilder()

    calendar_id = "cal_123"
    event_id = "example_event_id"
    event_uid = "external_event_id"
    event = {
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

    builder.delete_event(calendar_id, event_id)
    builder.delete_external_event(calendar_id, event_uid)
    builder.upsert_event(calendar_id, event)

    def request_callback(request):
        payload = json.loads(request.body)

        assert len(payload) == 3

        delete = payload[0]
        delete_external = payload[1]
        upsert = payload[2]

        assert delete['method'] == 'DELETE'
        assert delete['relative_url'] == '/v1/calendars/%s/events' % calendar_id
        assert delete['data']['event_id'] == event_id

        assert delete_external['method'] == 'DELETE'
        assert delete_external['relative_url'] == '/v1/calendars/%s/events' % calendar_id
        assert delete_external['data']['event_uid'] == event_uid

        assert upsert['method'] == 'POST'
        assert upsert['relative_url'] == '/v1/calendars/%s/events' % calendar_id

        assert upsert['data'] == event

        response = {
            "batch": [
                {"status": 202},
                {"status": 202},
                {"status": 202},
            ]
        }

        return (207, {}, json.dumps(response))

    responses.add_callback(
        responses.POST,
        url='%s/%s/batch' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    result = client.batch(builder)
    assert len(result.entries) == 3
    assert result.entries[0].request == {'data': {'event_id': 'example_event_id'}, 'method': 'DELETE', 'relative_url': '/v1/calendars/cal_123/events'}
    assert result.entries[0].response == {'status': 202}


@responses.activate
def test_batch_with_errors(client):
    builder = BatchBuilder()

    calendar_id = "cal_123"
    event_uid = "external_event_id"

    builder.delete_external_event(calendar_id, event_uid)
    builder.delete_external_event(calendar_id, event_uid)
    builder.delete_external_event(calendar_id, event_uid)

    def request_callback(request):
        response = {
            "batch": [
                {"status": 202},
                {"status": 202},
                {
                    "status": 422,
                    "data": {
                        "errors": {
                            "summary": [
                                {"key": "errors.required", "description": "summary must be specified"}
                            ]
                        }
                    }
                }
            ]
        }

        return (207, {}, json.dumps(response))

    responses.add_callback(
        responses.POST,
        url='%s/%s/batch' % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type='application/json',
    )

    try:
        client.batch(builder)
    except PyCronofyPartialSuccessError as e:
        assert e.message == 'Batch contains 1 errors'
