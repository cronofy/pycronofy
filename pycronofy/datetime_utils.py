import datetime
import pytz

def get_datetime_string(date_time, date=False):
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
    if type(date_time) in (type(''), type(u'')):
        return date_time
    elif type(date_time) not in (type(datetime.date.today()), type(datetime.datetime.now())):
        raise Exception('Unsupported type for get_datetime_string.\nSupported types: ``datetime.datetime``, ``datetime.date``, or ``string``.')
    if not date_time.tzinfo:
        raise Exception('tzinfo is None')
    if date:
        date_time.strftime('%Y-%m-%d') # ISO 8601 Format
    return date_time.strftime('%Y-%m-%dT%H:%M:%S%z') # ISO 8601 Format
