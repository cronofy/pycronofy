import pytest
import responses
from pycronofy import Client
from pycronofy import settings
from pycronofy.tests import common_data

@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    args = common_data.AUTH_ARGS.copy()
    args['data_center'] = 'de'
    return Client(**args)

@responses.activate
def test_userinfo_with_customer_data_center(client):
    """Test Client.userinfo().

    :param Client client: Client instance with test data.
    """
    expected_api = settings.API_REGION_FORMAT % 'de'

    responses.add(responses.GET,
        url='%s/%s/userinfo' % (expected_api, settings.API_VERSION),
        body='{"sub": "acc_5700a00eb0ccd07000000000", "cronofy.type": "userinfo"}',
        status=200,
        content_type='application/json',
    )
    userinfo = client.userinfo()
    assert userinfo['sub'] == 'acc_5700a00eb0ccd07000000000'
    assert userinfo['cronofy.type'] == 'userinfo'

@responses.activate
def test_user_auth_link_custom_data_center(client):
    """Test user auth link returns a properly formatted user auth url.

    :param Client client: Client instance with test data.
    """
    expected_app = settings.APP_REGION_FORMAT % 'de'

    querystring = 'scope=felines&state=NY&redirect_uri=http%%3A%%2F%%2Fexample.com&response_type=code&client_id=%s' % common_data.AUTH_ARGS['client_id']
    auth_url = '%s/oauth/authorize?%s' % (expected_app, querystring)

    url = client.user_auth_link(redirect_uri='http://example.com', scope='felines', state='NY')
    assert 'client_id=%s' % common_data.AUTH_ARGS['client_id'] in url

    url = client.user_auth_link(redirect_uri='http://example.com', state='NY')
    assert expected_app in url

