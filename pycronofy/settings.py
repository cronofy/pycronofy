# Settings for Cronofy Client

# API URL and Version 
API_BASE_URL = 'https://api.cronofy.com/'
API_VERSION = 'v1'

# Default Timezone ID (used in read_events)
DEFAULT_TIMEZONE_ID = 'Etc/UTC'

# Tuple of params required by the "events" endpoint.
# tzid isn't technically required, but should be specified to avoid subtle timezone bugs.
EVENTS_REQUIRED_FIELDS = ('event_id', 'summary', 'description', 'start', 'end', 'tzid')
