import requests
import pycronofy
from pycronofy import settings
from pycronofy.exceptions import PyCronofyRequestError


class RequestHandler(object):
    """Wrap all request handling."""

    def __init__(self, auth, data_center=None):
        """
        :param Auth auth: Auth instance.
        """
        self.auth = auth
        self.user_agent = '%s %s' % (pycronofy.__name__, pycronofy.__version__)
        if data_center is None or data_center == 'us':
            self.base_url = settings.API_BASE_URL
        else:
            self.base_url = settings.API_REGION_FORMAT % data_center

    def get(self, endpoint='', url='', params=None, use_api_key=False):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        return self._request('get', endpoint, url, params=params, use_api_key=use_api_key)

    def delete(self, endpoint='', url='', params=None, data=None):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :param dict data: Data to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        return self._request('delete', endpoint, url, params=params, data=data)

    def post(self, endpoint='', url='', data=None, use_api_key=False, omit_api_version=False):
        """Perform a post to an API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :return: Response.
        :rtype: ``Response``
        """
        return self._request('post', endpoint, url, data=data, use_api_key=use_api_key, omit_api_version=omit_api_version)

    def _request(self, request_method, endpoint='', url='', data=None, params=None, use_api_key=False, omit_api_version=False):
        """Perform a http request via the specified method to an API endpoint.

        :param string request_method: Request method.
        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :return: Response
        :rtype: ``Response``
        """
        if not data:
            data = {}
        if not params:
            params = {}
        if endpoint and omit_api_version and not url:
            url = '%s/%s' % (self.base_url, endpoint)
        if endpoint and not url:
            url = '%s/%s/%s' % (self.base_url, settings.API_VERSION, endpoint)

        if use_api_key:
            headers = {
                'Authorization': self.auth.get_api_key(),
                'User-Agent': self.user_agent,
            }
        else:
            headers = {
                'Authorization': self.auth.get_authorization(),
                'User-Agent': self.user_agent,
            }

        response = requests.__getattribute__(request_method)(
            url=url,
            hooks=settings.REQUEST_HOOK,
            headers=headers,
            json=data,
            params=params
        )
        if ((response.status_code != 200) and (response.status_code != 202)):
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise PyCronofyRequestError(
                    request=e.request,
                    response=e.response,
                )
        return response
