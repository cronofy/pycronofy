# Common test data used by multiple tests
import json
import responses

AUTH_ARGS = {
    'client_id': 'cats', 
    'client_secret': 'opposable thumbs', 
    'access_token': 'paw', 
    'refresh_token': 'teeth',
}

TEST_DATA_PAGE_ONE = {
  "pages": {
    "current": 1,
    "total": 2,
    "next_page": "https://api.cronofy.com/v1/events/pages/08a07b034306679e"
  },
  "events": [
    {
      "calendar_id": "cal_U9uuErStTG@EAAAB_IsAsykA2DBTWqQTf-f0kJw",
      "event_uid": "evt_external_54008b1a4a41730f8d5c6037",
      "summary": "Company Retreat",
      "description": "",
      "start": "2014-09-06",
      "end": "2014-09-08",
      "deleted": False,
      "location": {
        "description": "Beach"
      },
      "participation_status": "needs_action",
      "transparency": "opaque",
      "event_status": "confirmed",
      "categories": [],
      "attendees": [
        {
          "email": "example@cronofy.com",
          "display_name": "Example Person",
          "status": "needs_action"
        }
      ],
      "created": "2014-09-01T08:00:01Z",
      "updated": "2014-09-01T09:24:16Z"
    }
  ]
}

TEST_DATA_PAGE_TWO = {
  "pages": {
    "current": 2,
    "total": 2,
    "next_page": ""
  },
  "events": [
    {
      "calendar_id": "cal_U9uuErStTG@EAAAB_IsAsykA2DBTWqQTf-f0kJw",
      "event_uid": "evt_external_64008b1a4a41730f8d5c6057",
      "summary": "Company Retreat 2",
      "description": "",
      "start": "2014-10-06",
      "end": "2014-10-08",
      "deleted": False,
      "location": {
        "description": "Mountains"
      },
      "participation_status": "needs_action",
      "transparency": "opaque",
      "event_status": "confirmed",
      "categories": [],
      "attendees": [
        {
          "email": "example@cronofy.com",
          "display_name": "Example Person",
          "status": "needs_action"
        }
      ],
      "created": "2014-10-01T08:00:01Z",
      "updated": "2014-10-01T09:24:16Z"
    }
  ]
}

NEXT_PAGE_GET_ARGS = {
    'method': responses.GET, 
    'url': 'https://api.cronofy.com/v1/events/pages/08a07b034306679e',
    'body': json.dumps(TEST_DATA_PAGE_TWO),
    'status': 200,
    'content_type':'application/json'
}

TEST_EVENTS_ARGS = { 
    'url': 'https://api.cronofy.com/v1/events',
    'body': '{"example": 1}',
    'status': 200,
    'content_type':'application/json'
}