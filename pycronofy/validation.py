import datetime
import re

from pycronofy.exceptions import PyCronofyValidationError

# Matches ISO_8601 Cronofy accepts. Must be UTC if datetime.
ISO_8601_FORMATS = (
    r'(^\d\d\d\d\-\d\d-\d\d$)',
    r'(^\d\d\d\d\-\d\d-\d\dT\d\d\:\d\d\:\d\dZ$)',
    r'(^\d\d\d\d\-\d\d-\d\dT\d\d\:\d\d\:\d\dUTC)',
    r'(^\d\d\d\d\-\d\d-\d\dT\d\d\:\d\d\:\d\d\+00:00$)',
)
ISO_8601_REGEX = re.compile('|'.join(ISO_8601_FORMATS))

METHOD_RULES = {
    'account': {
        'args': (),
        'auth': ('access_token',),
    },
    'close_notification_channel': {
        'args': ('channel_id',),
        'auth': ('access_token',),
        'required': ('channel_id',),
    },
    'create_notification_channel': {
        'args': ('callback_url', 'calendar_ids', 'only_managed'),
        'auth': ('access_token',),
        'required': ('callback_url',),
    },
    'delete_event': {
        'args': ('calendar_id', 'event_id'),
        'auth': ('access_token',),
        'required': ('calendar_id', 'event_id'),
    },
    'get_authorization_from_code': {
        'args': ('code', 'redirect_uri'),
        'auth': ('client_id', 'client_secret'),
        'required': ('code',),
        'values': (
            ('redirect_uri', {'object': 'auth', 'key': 'redirect_uri'}),
        ),
    },
    'list_calendars': {
        'args': (),
        'auth': ('access_token',),
    },
    'list_profiles': {
        'args': (),
        'auth': ('access_token',),
    },
    'list_notification_channels': {
        'args': (),
        'auth': ('access_token',),
    },
    'read_events': {
        'args': ('calendar_ids', 'from_date', 'to_date', 'last_modified', 'tzid', 'only_managed',
                 'include_managed', 'include_deleted', 'include_moved', 'localized_times', 'automatic_pagination'),
        'auth': ('access_token',),
        'datetime': ('from_date', 'to_date', 'last_modified'),
    },
    'read_free_busy': {
        'args': ('calendar_ids', 'from_date', 'to_date', 'last_modified', 'tzid',
                 'include_managed', 'localized_times', 'automatic_pagination'),
        'auth': ('access_token',),
        'datetime': ('from_date', 'to_date', 'last_modified'),
    },
    'refresh_authorization': {
        'args': (),
        'auth': ('client_id', 'client_secret', 'refresh_token'),
    },
    'revoke_authorization': {
        'args': (),
        'auth': ('client_id', 'client_secret', 'access_token'),
    },
    'revoke_profile': {
        'args': ('profile_id',),
        'auth': ('access_token',),
        'required': ('profile_id',),
    },
    'upsert_event': {
        'args': ('calendar_id', 'event'),
        'auth': ('access_token',),
        'dicts': {
            'event': ('event_id', 'summary', 'description', 'start', 'end', 'tzid'),
        },
        'dicts_datetime': {
            'event': ('start', 'end',),
        },
        'required': ('calendar_id', 'event'),
    },
    'user_auth_link': {
        'args': ('redirect_uri', 'scope', 'state'),
        'auth': ('client_id',),
        'required': ('redirect_uri',),
    },
    'validate': {
        'args': ('method',),
        'required': ('method',),
    },
}


def check_exists_in_object(method, obj, required_fields):
    """Checks if required fields have a value in the object instance.
    Throws an exception with the missing fields.

    :param object obj: Object to check.
    :param typle required_fields: Required fields that must have a value.
    """
    missing = []
    for field in required_fields:
        if getattr(obj, field) is None:
            missing.append(field)
    if missing:
        raise PyCronofyValidationError('Method: %s. Missing auth field(s): %s' % (method, missing),
                                       method,
                                       missing
                                       )


def check_datetime(method, dictionary, fields, label=None):
    """Checks if the specified fields are formatted correctly if they have a value.
    Throws an exception on incorrectly formatted fields.

    :param dict dictionary: Dictionary to check.
    :param typle fields: Fields to check.
    :param string label: Dictionary name.
    """
    improperly_formatted = []
    values = []
    for field in fields:
        if field in dictionary and dictionary[field] is not None:
            if type(dictionary[field]) not in (datetime.datetime, datetime.date) and not ISO_8601_REGEX.match(dictionary[field]):
                improperly_formatted.append(field)
                values.append(dictionary[field])
    if improperly_formatted:
        error_label = ' for "%s"' % label if label else ''
        raise PyCronofyValidationError(
            'Method: %s. Improperly formatted datetime/date field(s)%s: %s\n%s' % (
                method, error_label, improperly_formatted, values),
            method,
            improperly_formatted,
            values
        )


def check_exists_in_dictionary(method, dictionary, required_fields, label=None):
    """Checks if required fields have a value in the object instance.
    Throws an exception with the missing fields.

    :param dict dictionary: Dictionary to check.
    :param typle required_fields: Required fields that must have a value.
    :param string label: Dictionary name.
    """
    missing = []
    for field in required_fields:
        if field not in dictionary or dictionary[field] is None:
            missing.append(field)
    if missing:
        error_label = ' for "%s"' % label if label else ''
        raise PyCronofyValidationError('Method: %s. Missing required field(s)%s: %s' % (method, error_label, missing),
                                       method,
                                       missing
                                       )


def validate(method, auth, *args, **kwargs):
    """Validate a method based on the METHOD_RULES above.

    Raises a PyCronofyValidationError on error.

    :param string method: Method being validated.
    :param Auth auth: Auth instance.
    :param *args: Positional arguments for method.
    :param **kwargs: Keyword arguments for method.
    """
    if method not in METHOD_RULES:
        raise PyCronofyValidationError('Method "%s" not found.' % method, method)

    m = METHOD_RULES[method]
    arguments = {}
    number_of_args = len(args)
    for i, key in enumerate(m['args']):
        if i < number_of_args:
            arguments[key] = args[i]
        elif key in kwargs:
            arguments[key] = kwargs[key]
        else:
            arguments[key] = None
    check_exists_in_object(method, auth, m['auth'])
    if 'required' in m:
        check_exists_in_dictionary(method, arguments, m['required'])
    if 'datetime' in m:
        check_datetime(method, arguments, m['datetime'])
    if 'dicts' in m:
        for d in m['dicts']:
            check_exists_in_dictionary(method, arguments[d], m['dicts'][d], d)
    if 'dicts_datetime' in m:
        for d in m['dicts_datetime']:
            check_datetime(method, arguments[d], m['dicts_datetime'][d], d)
