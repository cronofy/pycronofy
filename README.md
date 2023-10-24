## pycronofy

[![python CI](https://github.com/cronofy/pycronofy/actions/workflows/ci.yml/badge.svg)](https://github.com/cronofy/pycronofy/actions/workflows/ci.yml)

A python library for [Cronofy](http://www.cronofy.com)

Inspired by [Cronofy-Ruby](https://github.com/cronofy/cronofy-ruby)

[Developer API](http://www.cronofy.com/developers/api)

# Installation

**NOTE:** Support for Python v2.7 was dropped as of pycronofy v2.0.0

(unless performing a system wide install, it's recommended to install inside of a virtualenv)

```bash
# Install via pip:
pip install pycronofy

# Install via setup.py:
pip install -r requirements.txt # Install core & dependencies for tests
python setup.py install
```

---

# Authorization

OAuth tokens can be obtained for an application.

```python
import pycronofy

# Initial authorization
cronofy = pycronofy.Client(client_id=YOUR_CLIENT_ID, client_secret=YOUR_CLIENT_SECRET)

url = cronofy.user_auth_link('http://yourwebsite.com')
print('Go to this url in your browser, and paste the code below')

code = input('Paste Code Here: ') # raw_input() for python 2.
auth = cronofy.get_authorization_from_code(code)

# get_authorization_from_code updates the state of the cronofy client. It also returns
# the authorization tokens (and expiration) in case you need to store them.
# If that is the case, you will want to initiate the client as follows:
cronofy = pycronofy.Client(
    client_id=YOUR_CLIENT_ID,
    client_secret=YOUR_CLIENT_SECRET,
    access_token=auth['access_token'],
    refresh_token=auth['refresh_token'],
    token_expiration=auth['token_expiration']
)
```

Or alternatively with a personal access token.

```python
cronofy = pycronofy.Client(access_token=YOUR_TOKEN) # Using a personal token for testing.
```

Expiry of tokens can be verified with the is_authorization_expired method.

```python
cronofy.is_authorization_expired()
```

Data center can also be specified using the SDK ID from the docs: https://docs.cronofy.com/developers/data-centers/

```python
cronofy = pycronofy.Client(
    client_id=YOUR_CLIENT_ID,
    client_secret=YOUR_CLIENT_SECRET,
    access_token=auth['access_token'],
    refresh_token=auth['refresh_token'],
    token_expiration=auth['token_expiration'],
    data_center='us'
)
```

## Refreshing tokens

OAuth tokens can be refreshed using the refresh_authorization method.

```python
auth = cronofy.refresh_authorization()
```

## Revoking tokens

Tokens can be revoked using the revoke_authorization method.

```python
cronofy.revoke_authorization()
```

# Getting account info

```python
# For account details
cronofy.account()

# For userinfo
cronofy.userinfo()
```

# Listing profiles

```python
for profile in cronofy.list_profiles():
    print(profile)
```

# Listing calendars

```python
for calendar in cronofy.list_calendars():
    print(calendar)
```

# Reading events

```python
import datetime

# Example timezone id
timezone_id = 'US/Eastern'

# Dates/Datetimes must be in UTC
# For from_date, to_date, start, end, you can pass in a datetime object
# or an ISO 8601 datetime string.
# For example:
example_datetime_string = '2016-01-06T16:49:37Z' #ISO 8601.

# To set to local time, pass in the tzid argument.
from_date = (datetime.datetime.utcnow() - datetime.timedelta(days=2))
to_date = datetime.datetime.utcnow()
events = cronofy.read_events(calendar_ids=(YOUR_CAL_ID,),
    from_date=from_date,
    to_date=to_date,
    tzid=timezone_id # This argument sets the timezone to local, vs utc.
)

# Automatic pagination through an iterator
for event in events:
    print('%s (From %s to %s, %i attending)' %
        (event['summary'], event['start'], event['end'], len(event['attendees'])))

# Treat the events as a list (holding the current page only).
print(events[2])
print(len(events))

# Alternatively grab the actual list object for the current page:
page = events.current_page()
print(page[1])

# Manually move to the next page:
events.fetch_next_page()

# Access the raw data returned by the request:
events.json()

# Retrieve all data in a list:
# Option 1:
all_events = [event for event in cronofy.read_events(calendar_ids=(YOUR_CAL_ID,),
    from_date=from_date,
    to_date=to_date,
    tzid=timezone_id)
]

# Option 2:
all_events = cronofy.read_events(calendar_ids=(YOUR_CAL_ID,),
    from_date=from_date,
    to_date=to_date,
    tzid=timezone_id
).all()
```

# Free/Busy blocks

This method is essentially the same as reading events, but will only return free busy information.

```python
from_date = (datetime.datetime.utcnow() - datetime.timedelta(days=2))
to_date = datetime.datetime.utcnow()
free_busy_blocks = cronofy.read_free_busy(calendar_ids=(YOUR_CAL_ID,),
    from_date=from_date,
    to_date=to_date
)

for block in free_busy_blocks:
    print(block)
```

# Creating events

Create a event with local timezone.
(Note datetime objects or datetime strings must be UTC)
You need to supply a unique event id which you can then use to retreive the event with.

```python
import datetime
import uuid

# Example timezone id
timezone_id = 'US/Eastern'

event_id = 'example-%s' % uuid.uuid4(),

event = {
    'event_id': event_id,
    'summary': 'Test Event', # The event title
    'description': 'Discuss proactive strategies for a reactive world.',
    'start': datetime.datetime.utcnow(),
    'end': (datetime.datetime.utcnow() + datetime.timedelta(hours=1)),
    'tzid': timezone_id,
    'location': {
        'description': 'My Desk!',
    },
}

cronofy.upsert_event(calendar_id=cal['calendar_id'], event=event)
```

# Deletion

Events can be deleted in a number of ways

```python
# Delete using known event id
cronofy.delete_event(calendar_id=cal['calendar_id'], event_id=test_event_id)

# Delete all managed events (events inserted via Cronofy) for all user calendars.
cronofy.delete_all_events()

# Deletes all managed events for the specified user calendars.
cronofy.delete_all_events(calendar_ids=(CAL_ID,))
```

# Notification channels

Notification channels are used to receive push notifications informating your application of changes to calendars or profiles. This method requires an application and OAuth tokens, and will not work with a personal access token.

```python
channel = cronofy.create_notification_channel('http://example.com',
    calendar_ids=(cal['calendar_id'],)
)

# list channels
cronofy.list_notification_channels()

cronofy.close_notification_channel(channel['channel_id'])
```

---

# Validation

You can validate any pycronofy client call for:
Authentication, required arguments, datetime/date string format.
A PyCronofyValidationError will be thrown if there is an error.
Some examples:

```python
try:
    cronofy.validate('create_notification_channel', 'http://example.com',
        calendar_ids=(cal['calendar_id'],)
    )
except pycronofy.exceptions.PyCronofyValidationError as e:
    print(e.message)
    print(e.fields)
    print(e.method)
```

# Debugging

All requests will call response.raise_on_status if the response is not OK or ACCEPTED.
You can catch the exception and access the details.

```python
try:
    cronofy.upsert(event(calendar_id='ABC', event=malformed_event))
except pycronofy.exceptions.PyCronofyRequestError as e:
    print(e.response.reason) # Error Message
    print(e.response.text) # Response Body
    print(e.request.method) # HTTP Method
    print(e.request.headers) # Headers
    print(e.request.url) # URL and Get Data
    print(e.request.body) # Post Data

# pycronofy provides a "set_request_hook" argument to make use of requests' event hooks.

def on_request(response, *args, **kwargs):
    """
        "If the callback function returns a value,
        it is assumed that it is to replace the data that was passed in.
        If the function doesn’t return anything, nothing else is effected."
        http://docs.python-requests.org/en/latest/user/advanced/#event-hooks
    """
    print('%s %s' % (response.request.method, response.url))
    print(kwargs)

pycronofy.set_request_hook(on_request)
```

# Running the Unit Tests

```bash
py.test pycronofy --cov=pycronofy
```

# Dependencies

Core library depends on ``requests``.

Tests depend on ``pytest, pytest-cov, responses``.

# Notes

In the event of an insecure platform warning:

* Install python >= 2.7.9
* pip install requests\[security\] (you may need to install additional library packages)
* Call ``requests.packages.urllib3.disable_warnings()`` in your code to suppress the warnings.

## A feature I want is not in the SDK, how do I get it?

We add features to this SDK as they are requested, to focus on developing the Cronofy API.

If you're comfortable contributing support for an endpoint or attribute, then we love to receive pull requests!
Please create a PR mentioning the feature/API endpoint you’ve added and we’ll review it as soon as we can.

If you would like to request a feature is added by our team then please let us know by getting in touch via [support@cronofy.com](mailto:support@cronofy.com).
