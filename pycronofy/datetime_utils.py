import datetime
import pytz

from pycronofy.exceptions import PyCronofyDateTimeError

ISO_8601_DATE_FORMAT = '%Y-%m-%d'
ISO_8601_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'  # UTC


def format_event_time(date_time):
    """
        Accepts either an ISO 8601 string, a dict with a time and tzid OR a datetime object.
        Must be in UTC format:

        2016-01-31T12:33:00Z
        2016-01-31T12:33:00UTC
        2016-01-31T12:33:00+00:00

        https://en.wikipedia.org/wiki/ISO_8601

        :param datetime.datetime date_time: ``datetime.datetime``, ``dict`` or ``string``.
        :return: ISO 8601 formatted datetime string.
        :rtype: ``string`` or ``dict``
    """
    if not date_time:
        # Return None if passed None
        return date_time
    date_time_type = type(date_time)
    if date_time_type in (type(''), type(u'')):
        # If passed a string, return the string.
        return date_time
    elif date_time_type == datetime.date:
        # If passed a date, return an iso8601 formatted date string.
        return date_time.strftime(ISO_8601_DATE_FORMAT)
    elif date_time_type is dict:
        if date_time.get('time'):
            date_time['time'] = format_event_time(date_time['time'])
        return date_time
    elif date_time_type != datetime.datetime:
        # If passed anything other than a datetime, date, string, dict, or None, raise an Exception.
        error_message = 'Unsupported type: ``%s``.\nSupported types: ``<datetime.datetime>``, ``<datetime.date>``, ``<dict>``, or ``<str>``.'
        raise PyCronofyDateTimeError(
            error_message % (repr(type(date_time))), date_time)
    if date_time.tzinfo and date_time.tzinfo != pytz.utc:
        date_time = date_time.astimezone(pytz.utc)
    return date_time.strftime(ISO_8601_DATETIME_FORMAT)
