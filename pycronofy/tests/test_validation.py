import pytest
from pycronofy.auth import Auth
from pycronofy.exceptions import PyCronofyValidationError
from pycronofy.validation import check_attr, check_datetime, check_dict, validate


def test_check_attr():
    """Test if check_attr throws an exception if a required field isn't found."""
    class Pets(object):
        cat = None
        dog = None
    a = Pets()
    a.cat = 'Maru'
    check_attr('read_events', a, ('cat',))
    with pytest.raises(PyCronofyValidationError) as exception_info:
        check_attr('read_events', a, ('dog',))
    assert 'dog' in exception_info.value.fields

def test_check_datetime():
    """Test if check_datetime throws an exception if an improperly formatted datetime is found."""
    a = {
        'start':'2016-12-30T11:30:00Z',
    }
    check_datetime('upsert_event', a, ('start',))
    a = {
        'start':'2016-12-30T11:30:00+4506',
    }
    with pytest.raises(PyCronofyValidationError) as exception_info:
        check_datetime('upsert_event', a, ('start',))
    assert 'start' in exception_info.value.fields
    a = {
        'start':'2016-12-30 11:30:00Z',
    }
    with pytest.raises(PyCronofyValidationError) as exception_info:
        check_datetime('upsert_event', a, ('start',))
    assert 'start' in exception_info.value.fields

def test_check_dict():
    """Test if check_dict throws an exception if a required field isn't found."""
    a = {}
    a['cat'] = 'Maru'
    check_dict('read_events', a, ('cat',))
    with pytest.raises(PyCronofyValidationError) as exception_info:
        check_dict('read_events', a, ('dog',))
    assert 'dog' in exception_info.value.fields

def test_validate():
    """Test if validate properly validates methods."""
    auth = Auth(access_token='access')
    validate('create_notification_channel', auth, 'http://example.com', 
        calendar_ids=('id',),
    )
    with pytest.raises(PyCronofyValidationError) as exception_info:
        validate('create_notification_channel', auth)
    assert 'callback_url' in exception_info.value.fields
    with pytest.raises(PyCronofyValidationError) as exception_info:
        validate('create_notification_channel', Auth(), 'http://example.com', 
            calendar_ids=('id',)
        )
    assert 'access_token' in exception_info.value.fields
