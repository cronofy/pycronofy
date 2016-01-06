## PyCronofy ##

A minimalist python library for [Cronofy](http://www.cronofy.com)

Inspired by [Cronofy-Ruby](https://github.com/cronofy/cronofy-ruby)

[Developer API](http://www.cronofy.com/developers/api)

Usage:

```python
import datetime
import uuid
import pytz
from pycronofy import CronofyClient

cronofy = CronofyClient(access_token=YOUR_TOKEN) # Using a personal token for testing.

timezone_id = 'America/New_York'

# Get first calendar
print(cronofy.list_calendars()[0])

# For from_date, to_date, start, end, you can pass in a datetime object or an ISO 8601 datetime string with the offset included.
# For example:
example_datetime_string = '2016-01-06T16:49:37-0456' #ISO 8601 with offset.

# Getting events with UTC
from_date = (datetime.datetime.utcnow() - datetime.timedelta(days=2))
to_date = datetime.datetime.utcnow()
events = cronofy.read_events(calendar_ids=(YOUR_CAL_ID,), from_date=from_date, to_date=to_date)

# Getting events with local timezone
from_date = (datetime.datetime.now() - datetime.timedelta(days=2)).replace(tzinfo=pytz.timezone(timezone_id))
to_date = datetime.datetime.now().replace(tzinfo=pytz.timezone(timezone_id))
events = cronofy.read_events(calendar_ids=(YOUR_CAL_ID,), from_date=from_date, to_date=to_date, tzid=timezone_id)

# Automatic pagination through an iterator
for event in events:
    print('%s (From %s to %s, %i attending)' % (event['summary'], event['start'], event['end'], len(event['attendees'])))

# Create a test event with local timezone
event = {
    'event_id': 'example-%s' % uuid.uuid4(), # You need to supply a uuid, most likely from your system.
    'summary': 'Test Event', # The event title
    'description': 'Discuss proactive strategies for a reactive world.',
    'start': datetime.datetime.now().replace(tzinfo=pytz.timezone(timezone_id)),
    'end': (datetime.datetime.now() + datetime.timedelta(hours=1)).replace(tzinfo=pytz.timezone(timezone_id)),
    'tzid': timezone_id,
    'location': {
        'description': 'My Desk!',
    },
}
print(cronofy.upsert_event(calendar_id=cal['calendar_id'], event=event))
```
