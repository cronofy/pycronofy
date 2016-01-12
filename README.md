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

# Example timezone id
timezone_id = 'America/New_York'

#######################
# Authorization:
#######################

### With a personal access token
cronofy = CronofyClient(access_token=YOUR_TOKEN) # Using a personal token for testing.

### With OAuth
cronofy = CronofyClient(client_id=YOUR_CLIENT_ID, client_secret=YOUR_CLIENT_SECRET)

response = cronofy.user_auth_link('http://yourwebsite.com')
print('Go to this url in your browser, and paste the code below')
print(response.url)
code = input('Paste Code Here: ')
cronofy.authorize_from_code(code)

#######################
# Getting a calendar
#######################

print(cronofy.list_calendars()[0])

#######################
# Getting events
#######################

# For from_date, to_date, start, end, you can pass in a datetime object 
# or an ISO 8601 datetime string with the offset included.
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

# Treat the events as a list (holding the current page only).
print(events[2])
print(len(events))

# Alternatively grab the actual list object for the current page:
page = events.current_page()
print(page[1])

# Manually move to the next page:
events.fetch_next_page()

# Access the raw data returned by the request:
events.data()

# Retrieve all data in a list:
# Option 1:
all = [event for event in cronofy.read_events(calendar_ids=(YOUR_CAL_ID,), from_date=from_date, to_date=to_date, tzid=timezone_id)]

# Option 2:
all = cronofy.read_events(calendar_ids=(YOUR_CAL_ID,), from_date=from_date, to_date=to_date, tzid=timezone_id).all()

#######################
# Creating a test event
#######################

# Create a test event with local timezone
test_event_id = 'example-%s' % uuid.uuid4(), # You need to supply a uuid, most likely from your system.
event = {
    'event_id': test_event_id
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

#######################
# Deleting a test event
#######################

print(cronofy.delete_event(calendar_id=cal['calendar_id'], event_id=test_event_id))
```
