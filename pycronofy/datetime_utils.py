import datetime

ISO_8601_DATE_FORMAT = '%Y-%m-%d'
ISO_8601_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

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
        raise Exception('Unsupported type for get_datetime_string.\nSupported types: ``datetime.datetime``, ``datetime.date``, or ``string``.')
    elif not date_time.tzinfo:
        # If there is a date/datetime object ensure there tzinfo has been set.
        raise Exception('tzinfo is None')
    return date_time.strftime(ISO_8601_DATETIME_FORMAT)
