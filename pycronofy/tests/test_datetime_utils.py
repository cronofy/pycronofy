import datetime
import pytest
import pytz
from pycronofy.datetime_utils import format_event_time


def test_date():
    """Test format_event_time returns an ISO8601 formatted date string when passed a datetime.date object"""
    assert format_event_time(datetime.date(2016, 1, 15)) == '2016-01-15'


def test_date_nested_in_dict():
    """Test format_event_time returns an ISO8601 formatted date string in a dict when passed a datetime.date object"""
    date = datetime.date(2016, 1, 15)
    params = {
        'time': date,
        'tzid': 'Etc/UTC',
    }
    assert format_event_time(params) == {'time': '2016-01-15', 'tzid': 'Etc/UTC'}


def test_iso8601_string_in_dict():
    """Test format_event_time returns an ISO8601 formatted date string in a dict when passed a iso8601 string"""
    date = '2016-01-15'
    params = {
        'time': date,
        'tzid': 'Etc/UTC',
    }
    assert format_event_time(params) == {'time': '2016-01-15', 'tzid': 'Etc/UTC'}


def test_tz_aware_datetime_in_dict():
    """Test format_event_time returns an ISO8601 formatted date string in a dict when passed a datetimee object"""
    date = datetime.datetime(2016, 1, 15, 14, 20, 15, tzinfo=pytz.timezone('EST'))
    params = {
        'time': date,
        'tzid': 'Etc/UTC',
    }
    assert format_event_time(params) == {'time': '2016-01-15T19:20:15Z', 'tzid': 'Etc/UTC'}


def test_datetime():
    """Test format_event_time returns an ISO8601 formatted datetime string when passed a datetime.date object,
    and throws an exception when tzinfo is not set."""
    target_datetime = '2016-01-15T09:08:00'
    d = datetime.datetime.strptime(target_datetime, '%Y-%m-%dT%H:%M:%S')
    assert format_event_time(d) == ('%sZ' % target_datetime)


def test_iso8601_string():
    """Test format_event_time returns a string when passed a string"""
    assert format_event_time('2016-01-15') == '2016-01-15'


def test_none():
    """Test format_event_time returns None when passed None"""
    assert format_event_time(None) is None


def test_tz_aware_datetime():
    """Test format_event_time returns an ISO8601 formatted datetime string with UTC timezone
    when passed a datetime.date object that's set to another timezone."""
    d = datetime.datetime(2016, 1, 15, 14, 20, 15, tzinfo=pytz.timezone('EST'))
    assert format_event_time(d) == '2016-01-15T19:20:15Z'


def test_unsupported():
    """Test format_event_time throws an exception when passed an unsupported type"""
    with pytest.raises(Exception) as exception_info:
        format_event_time(1)
    assert exception_info.value.message == 'Unsupported type: ``%s``.\nSupported types: ``<datetime.datetime>``, ``<datetime.date>``, ``<dict>``, or ``<str>``.' % repr(type(1))
    assert exception_info.value.argument == 1
