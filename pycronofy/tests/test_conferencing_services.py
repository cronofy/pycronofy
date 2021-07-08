import json

import pytest
import responses

from pycronofy import Client, settings
from pycronofy.tests import common_data

TEST_CONFERENCING_SERVICES_AUTHORIZATION_URL = (
    "https://app.cronofy.com/conferencing_services/xxxxx"
)
TEST_CONFERENCING_SERVICES_AUTHORIZATION_RESPONSE = {
    "authorization_request": {"url": TEST_CONFERENCING_SERVICES_AUTHORIZATION_URL}
}


@pytest.fixture(scope="module")
def client():
    """Setup Client instance with test values."""
    return Client(**common_data.AUTH_ARGS)


@responses.activate
def test_conferencing_services_auth_link(client):
    def request_callback(request):
        payload = json.loads(request.body)
        assert payload["redirect_uri"] == "https://redirect.here.please/"

        return (200, {}, json.dumps(TEST_CONFERENCING_SERVICES_AUTHORIZATION_RESPONSE))

    responses.add_callback(
        responses.POST,
        url="%s/%s/conferencing_service_authorizations"
        % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type="application/json",
    )

    auth_link = client.get_conferencing_services_auth_link("https://redirect.here.please/")

    assert auth_link == TEST_CONFERENCING_SERVICES_AUTHORIZATION_URL


@responses.activate
def test_conferencing_services_auth_link_with_provider(client):
    def request_callback(request):
        payload = json.loads(request.body)
        assert payload["redirect_uri"] == "https://redirect.here.please/"
        assert payload["provider_name"] == "zoom"

        return (200, {}, json.dumps(TEST_CONFERENCING_SERVICES_AUTHORIZATION_RESPONSE))

    responses.add_callback(
        responses.POST,
        url="%s/%s/conferencing_service_authorizations"
        % (settings.API_BASE_URL, settings.API_VERSION),
        callback=request_callback,
        content_type="application/json",
    )

    auth_link = client.get_conferencing_services_auth_link("https://redirect.here.please/", provider_name="zoom")

    assert auth_link == TEST_CONFERENCING_SERVICES_AUTHORIZATION_URL
