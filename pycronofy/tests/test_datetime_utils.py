import datetime
from ..datetime_utils import get_iso8601_string

# UTC tzinfo class to remove pytz dependency only used in tests:
class UTC(datetime.tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return datetime.timedelta(0)
# End UTC class

def test_none():
    """Test get_iso8601_string returns None when passed None"""
    assert get_iso8601_string(None) == None

def test_iso8601_string():
    """Test get_iso8601_string returns a string when passed a string"""
    assert get_iso8601_string('2016-01-15') == '2016-01-15'

def test_date():
    """Test get_iso8601_string returns an ISO8601 formatted date string when passed a datetime.date object"""
    assert get_iso8601_string(datetime.date(2016, 1, 15)) == '2016-01-15'

def test_datetime():
    """Test get_iso8601_string returns an ISO8601 formatted datetime string when passed a datetime.date object"""
    target_datetime = '2016-01-15T09:08:00'
    d = datetime.datetime.strptime(target_datetime, '%Y-%m-%dT%H:%M:%S')
    d = d.replace(tzinfo=UTC())
    assert get_iso8601_string(d) == ('%s+0000' % target_datetime)