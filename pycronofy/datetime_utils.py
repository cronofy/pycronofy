import datetime
import pytz

ISO_8601_DATE_FORMAT = '%Y-%m-%d'
ISO_8601_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

def get_iso8601_string(date_time, date=False):
    """
        Accepts either an ISO 8601 string OR a datetime object.
        DateTime objects must have a tzinfo defined.

        https://en.wikipedia.org/wiki/ISO_8601

        :param datetime.datetime date_time: ``datetime.datetime`` or ``string``.
        :return: ISO 8601 formatted datetime string.
        :rtype: ``string`` 
    """
    # Return None if passed None
    if not date_time:
        return date_time
    # If passed a string, return the string.
    elif type(date_time) in (type(''), type(u'')):
        return date_time
    # If passed anything other than a datetime, date, string, or None, raise an Exception.
    elif type(date_time) not in (type(datetime.date.today()), type(datetime.datetime.now())):
        raise Exception('Unsupported type for get_datetime_string.\nSupported types: ``datetime.datetime``, ``datetime.date``, or ``string``.')
    # If there is a date/datetime object ensure there tzinfo has been set.
    if not date_time.tzinfo:
        raise Exception('tzinfo is None')
    if date:
        date_time.strftime(ISO_8601_DATE_FORMAT)
    return date_time.strftime(ISO_8601_DATE_FORMAT)
