import pytest
import responses
import requests
from pycronofy.auth import Auth
from pycronofy import settings
import test_data

@pytest.fixture(scope="module")
def auth():
    """Setup Auth instance with test values."""
    return Auth(**test_data.AUTH_ARGS)

def test_get_authorization(auth):
    """Test get_authorization returns the correct Authorization header value.

    :param Auth auth: Auth instance with test data.
    """
    assert auth.get_authorization() == 'Bearer %s' % test_data.AUTH_ARGS['access_token']

@responses.activate
def test_refresh(auth):
    """Test refresh updates the access_token, expires_in, and authorization_datetime.

    :param Auth auth: Auth instance with test data.
    """
    responses.add(responses.POST, 
        '%s/oauth/token' % settings.API_BASE_URL,
        body='{"access_token": "tail", "expires_in": 3600}', 
        status=200,
        content_type='application/json'
    )
    old_auth_datetime = auth.authorization_datetime
    response = auth.refresh()
    assert response.status_code == requests.codes.ok
    assert auth.access_token == 'tail'
    assert auth.expires_in == 3600
    assert auth.authorization_datetime > old_auth_datetime

@responses.activate
def test_revoke(auth):
    """Test revoke sets the access_token, refresh_token and authorization_datetime to None and the expires_in to 0.

    :param Auth auth: Auth instance with test data.
    """
    responses.add(responses.POST, 
        '%s/oauth/token/revoke' % settings.API_BASE_URL,
        status=200,
        content_type='application/json'
    )
    response = auth.revoke()
    assert response.status_code == requests.codes.ok
    assert auth.access_token == None
    assert auth.refresh_token == None
    assert auth.expires_in == 0
    assert auth.authorization_datetime == None

@responses.activate
def test_update_tokens_from_code(auth):
    """Test update_tokens_from code updates access_token, refresh_token, authorization_datetime and expires_in.

    :param Auth auth: Auth instance with test data.
    """
    responses.add(responses.POST, 
        '%s/oauth/token' % settings.API_BASE_URL,
        body='{"access_token": "tail", "refresh_token": "meow", "expires_in": 3600}', 
        status=200,
        content_type='application/json'
    )
    response = auth.update_tokens_from_code('code')
    assert response.status_code == requests.codes.ok
    assert auth.access_token == 'tail'
    assert auth.refresh_token == 'meow'
    assert auth.expires_in == 3600

@responses.activate
def test_user_auth_link(auth):
    """Test user auth link returns a properly formatted user auth url.

    :param Auth auth: Auth instance with test data.
    """
    querystring = 'scope=felines&state=NY&redirect_uri=http%%3A%%2F%%2Fexample.com&response_type=code&client_id=%s' % test_data.AUTH_ARGS['client_id']
    responses.add(responses.GET, 
        '%s/oauth/authorize' % settings.APP_BASE_URL,
        status=200,
        content_type='application/json'
    )
    response = auth.user_auth_link(redirect_uri='http://example.com', scope='felines', state='NY')
    assert response.status_code == requests.codes.ok
    assert response.url == '%s/oauth/authorize?%s' % (settings.APP_BASE_URL, querystring)

