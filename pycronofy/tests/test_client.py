import pytest
import responses
import requests
from ..auth import Auth
from .. import settings

@pytest.fixture(scope="module")
def auth():
    return Auth(client_id='cats', client_secret='opposable thumbs', access_token='paw', refresh_token='teeth')