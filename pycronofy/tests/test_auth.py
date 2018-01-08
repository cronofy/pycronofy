import pytest
from pycronofy.auth import Auth
from pycronofy.tests import common_data


@pytest.fixture(scope="module")
def auth():
    """Setup Auth instance with test values."""
    return Auth(**common_data.AUTH_ARGS)


def test_get_authorization(auth):
    """Test get_authorization returns the correct Authorization header value.

    :param Auth auth: Auth instance with test data.
    """
    assert auth.get_authorization() == 'Bearer %s' % common_data.AUTH_ARGS['access_token']


def test_get_api_key(auth):
    """Test get_api_keyireturns the correct Authorization header value.

    :param Auth auth: Auth instance with test data.
    """
    assert auth.get_api_key() == 'Bearer %s' % common_data.AUTH_ARGS['client_secret']
