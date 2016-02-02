import datetime

ISO_8601_DATE_FORMAT = '%Y-%m-%d'
ISO_8601_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

class PyCronofyDateTimeError(Exception):
    def __init__(self, message, argument):
        """
        :param string message: Exception message.
        :param object argument: Value passed into get_iso8601_string.
        """
        super(PyCronofyDateTimeError, self).__init__(message)
        self.argument = argument

class UTC(datetime.tzinfo):
    """UTC tzinfo class to remove pytz dependency."""
    def utcoffset(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return datetime.timedelta(0)

def get_iso8601_string(date_time):
    """
        Accepts either an ISO 8601 string OR a datetime object.
        DateTime objects must have a tzinfo defined.

        https://en.wikipedia.org/wiki/ISO_8601

        :param datetime.datetime date_time: ``datetime.datetime`` or ``string``.
        :return: ISO 8601 formatted datetime string.
        :rtype: ``string``
    """
    if not date_time:
        # Return None if passed None
        return date_time
    date_time_type = type(date_time)
    if date_time_type in (type(''), type(u'')):
        # If passed a string, return the string.
        return date_time
    elif date_time_type == type(datetime.date.today()):
        # If passed a date, return an iso8601 formatted date string.
        return date_time.strftime(ISO_8601_DATE_FORMAT)
    elif date_time_type != type(datetime.datetime.now()):
        # If passed anything other than a datetime, date, string, or None, raise an Exception.
        error_message = 'Unsupported type: ``%s``.\nSupported types: ``<datetime.datetime>``, ``<datetime.date>``, or ``<str>``.'
        raise PyCronofyDateTimeError(error_message % (repr(type(date_time))), date_time)
    elif not date_time.tzinfo:
        # If there is a date/datetime object ensure there tzinfo has been set.
        raise PyCronofyDateTimeError('tzinfo is None', date_time)
    return date_time.strftime(ISO_8601_DATETIME_FORMAT)
