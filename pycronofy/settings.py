# Settings for Cronofy Client

# API URL and Version 
API_BASE_URL = 'https://api.cronofy.com'
APP_BASE_URL = 'https://app.cronofy.com'
API_VERSION = 'v1'

# Turned into a space separated string
DEFAULT_OAUTH_SCOPE = (
    'read_account',
    'list_calendars',
    'read_account',
    'read_events',
    'create_event',
    'delete_event',
    'read_free_busy',
    )

# Default Timezone ID (used in read_events)
DEFAULT_TIMEZONE_ID = 'Etc/UTC'

# Tuple of params required by the "events" endpoint.
# tzid isn't technically required, but should be specified to avoid subtle timezone bugs.
EVENTS_REQUIRED_FIELDS = ('event_id', 'summary', 'description', 'start', 'end', 'tzid')
