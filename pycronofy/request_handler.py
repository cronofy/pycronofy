import requests
from pycronofy import settings

class RequestHandler(object):
    """Wrap all request handling.
    """

    def __init__(self, auth):
        """

        :param Auth auth: Auth instance.
        """
        self.auth = auth

    def get(self, endpoint='', url='', params={}, return_json=True):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        return self._request('get', endpoint, url, params=params, return_json=return_json)

    def delete(self, endpoint='', url='', params={}):
        """Perform a get for a json API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :return: Response json.
        :rtype: ``dict``
        """
        return self._request('delete', endpoint, url, params=params)

    def post(self, endpoint='', url='', data={}):
        """Perform a post to an API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :return: Response.
        :rtype: ``Response``
        """
        return self._request('post', endpoint, url, data=data)

    def _request(self, request_method, endpoint='', url='', data={}, params={}, return_json=False):
        """Perform a http request via the specified method to an API endpoint.

        :param string endpoint: Target endpoint. (Optional).
        :param string url: Override the endpoint and provide the full url (eg for pagination). (Optional).
        :param dict params: Provide parameters to pass to the request. (Optional).
        :param dict data: Data to pass to the post. (Optional).
        :param bool return_json: Return json instead of the Response object. (Optional, default False).
        :return: Response or Response json
        :rtype: ``Response`` or ``dict``
        """
        if endpoint and not url:
            url = '%s/%s/%s' % (settings.API_BASE_URL, settings.API_VERSION, endpoint)
        if settings.DEBUG:
            print('Request (%s): %s' % (request_method, url))
        if data:
            response = requests.__getattribute__(request_method)(url, headers={'Authorization': self.auth.get_authorization()}, json=data)
        else:
            response = requests.__getattribute__(request_method)(url, headers={'Authorization': self.auth.get_authorization()}, params=params)
        if response.status_code not in (requests.codes.ok, requests.codes.accepted):
            response.raise_for_status()
        if return_json:
            return response.json()
        return response