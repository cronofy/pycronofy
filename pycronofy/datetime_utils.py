import datetime
import pytz

def get_datetime_string(date_time):
    """
        Accepts either an ISO 8601 string OR a datetime object.
        DateTime objects must have a tzinfo defined.

        https://en.wikipedia.org/wiki/ISO_8601

        :param datetime.datetime date_time: ``datetime.datetime`` or ``string``.
        :return: ISO 8601 formatted datetime string.
        :rtype: ``string`` 
    """
    if not date_time:
        return date_time
    if type(date_time) == type(''):
        return date_time
    elif type(date_time) != type(datetime.datetime.now()):
        raise Exception('Unsupported type for get_datetime_string.\nSupported types: ``datetime.datetime`` or ``string``.')
    if not date_time.tzinfo:
        raise Exception('tzinfo is None')
    return date_time.strftime('%Y-%m-%dT%H:%M:%S%z') # ISO 8601 Format
