from pycronofy.datetime_utils import format_event_time


class BatchBuilder(object):
    def __init__(self):
        self.entries = list()

    def upsert_event(self, calendar_id, event):
        data = event.copy()

        event['start'] = format_event_time(event['start'])
        event['end'] = format_event_time(event['end'])

        self.post("/v1/calendars/%s/events" % calendar_id, data)
        return self

    def delete_event(self, calendar_id, event_id):
        self.delete("/v1/calendars/%s/events" %
                    calendar_id, data={'event_id': event_id})
        return self

    def delete_external_event(self, calendar_id, event_uid):
        self.delete("/v1/calendars/%s/events" %
                    calendar_id, data={'event_uid': event_uid})
        return self

    def add_entry(self, method, relative_url, data):
        self.entries.append(BatchEntryRequest(method, relative_url, data))

    def build(self):
        return list(map(lambda entry: entry.to_dict(), self.entries))

    def delete(self, relative_url, data):
        self.add_entry(method="DELETE", relative_url=relative_url, data=data)

    def post(self, relative_url, data):
        self.add_entry(method="POST", relative_url=relative_url, data=data)


class BatchEntry(object):
    def __init__(self, request, response):
        self.request = request
        self.response = response

    def status(self):
        return self.response['status']


class BatchEntryRequest(object):
    def __init__(self, method, relative_url, data):
        self.method = method
        self.relative_url = relative_url
        self.data = data

    def to_dict(self):
        return {'method': self.method, 'relative_url': self.relative_url, 'data': self.data}


class BatchResponse(object):
    def __init__(self, entries):
        self.entries = entries

    def errors(self):
        return list(filter(lambda entry: (entry.status() % 100) != 2, self.entries))

    def has_errors(self):
        return len(self.errors()) > 0
