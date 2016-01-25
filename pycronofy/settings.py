# Settings for Cronofy Client

# API URL and Version 
API_BASE_URL = 'https://api.cronofy.com'
APP_BASE_URL = 'https://app.cronofy.com'
API_VERSION = 'v1'

# Turned into a space separated string
DEFAULT_OAUTH_SCOPE = (
    'read_account',
    'list_calendars',
    'read_events', 
    'create_event',
    'delete_event',
    # 'read_free_busy', # implicitly included by 'read_events'
    )

# Default Timezone ID (used in read_events)
DEFAULT_TIMEZONE_ID = 'Etc/UTC'

# Tuple of params required by the "events" endpoint.
# tzid isn't technically required, but should be specified to avoid subtle timezone bugs.
EVENTS_REQUIRED_FIELDS = ('event_id', 'summary', 'description', 'start', 'end', 'tzid')

# If set to True, print out additional debugging info (such as urls for requests).
# This will also work if you are testing code that calls pycronofy without needing to alter that code.
"""
Example:

import pycronofy
pycronofy.settings.DEBUG = True
# Code you want to executre with debug on.
"""
DEBUG = False