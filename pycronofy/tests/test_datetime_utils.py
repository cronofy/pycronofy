import datetime
import pytest
from pycronofy.datetime_utils import get_iso8601_string, UTC

def test_date():
    """Test get_iso8601_string returns an ISO8601 formatted date string when passed a datetime.date object"""
    assert get_iso8601_string(datetime.date(2016, 1, 15)) == '2016-01-15'

def test_datetime():
    """Test get_iso8601_string returns an ISO8601 formatted datetime string when passed a datetime.date object,
    and throws an exception when tzinfo is not set."""
    target_datetime = '2016-01-15T09:08:00'
    d = datetime.datetime.strptime(target_datetime, '%Y-%m-%dT%H:%M:%S')
    with pytest.raises(Exception) as exception_info:
        get_iso8601_string(d)
    assert exception_info.value.message == 'tzinfo is None'
    d = d.replace(tzinfo=UTC())
    assert get_iso8601_string(d) == ('%s+0000' % target_datetime)

def test_iso8601_string():
    """Test get_iso8601_string returns a string when passed a string"""
    assert get_iso8601_string('2016-01-15') == '2016-01-15'

def test_none():
    """Test get_iso8601_string returns None when passed None"""
    assert get_iso8601_string(None) == None

def test_unsupported():
    """Test get_iso8601_string throws an exception when passed an unsupported type"""
    with pytest.raises(Exception) as exception_info:
        get_iso8601_string(1)
    assert exception_info.value.message == 'Unsupported type for get_datetime_string.\nSupported types: ``datetime.datetime``, ``datetime.date``, or ``string``.'
