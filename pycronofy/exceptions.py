class PyCronofyDateTimeError(Exception):
    """Exception class for datetime_utils improper argument."""
    def __init__(self, message, argument):
        """
        :param string message: Exception message.
        :param object argument: Value passed into get_iso8601_string.
        """
        super(PyCronofyDateTimeError, self).__init__(message)
        self.argument = argument

class PyCronofyRequestError(Exception):
    """Wraps requests.exceptions.HTTPError for convenience and give a little more info in the message."""
    def __init__(self, request, response):
        """
        :param Request request: requests.Request.
        :param Response response: responses.Response.
        """
        body = ''
        if request.method in ('POST', 'PUT') and request.body:
            body = '\nPOST data: %s' % request.body
        message = 'Response: %(status_code)s: %(reason)s\nRequest: %(method)s %(url)s%(body)s%(text)s' % {
            'status_code': response.status_code,
            'reason': response.reason,
            'text': ('\n%s' % response.text) if response.text else '',
            'method': request.method,
            'url': request.url,
            'body': body,
        }
        super(PyCronofyRequestError, self).__init__(message)
        self.message = message
        self.request = request
        self.response = response

class PyCronofyValidationError(Exception):
    """Exception class for validation errors with client.Client methods."""
    def __init__(self, message, method, fields=None, values=None):
        """
        :param string message: Exception message.
        :param string method: Method being validated.
        :param string fields: Invalid fields. (Optional, None by default).
        :param string values: Invalid field values (will be None if error fields do not exist). (Optional, None by default).
        """
        super(PyCronofyValidationError, self).__init__(message)
        self.method = method
        self.fields = fields
        self.values = values
