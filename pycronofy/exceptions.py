class PyCronofyDateTimeError(Exception):
    """Exception class for datetime_utils improper argument."""

    def __init__(self, message, argument):
        """
        :param string message: Exception message.
        :param object argument: Value passed into format_event_time.
        """
        super(PyCronofyDateTimeError, self).__init__(message)
        self.argument = argument
        self.message = message


class PyCronofyRequestError(Exception):
    """Wraps requests.exceptions.HTTPError for convenience and give a little more info in the message."""

    def __init__(self, request, response):
        """
        :param Request request: requests.Request.
        :param Response response: responses.Response.
        """
        body = ''
        if request.method in ('POST', 'PUT', 'PATCH') and request.body:
            body = '\nRequest Body: %s' % request.body
        headers = request.headers
        headers.pop('Authorization')
        # Message leaves out request.headers['Authorization'] for security reasons.
        # This can be accessed via the exception:
        # exception_instance.request.headers['Authorization']
        message = 'Response: %(status_code)s: %(reason)s\nRequest: %(method)s %(url)s\nRequest Headers:%(headers)s%(body)s%(content)s' % {
            'body': body,
            'content': ('\nResponse Content:\n%s' % response.content) if response.content else '',
            'headers': headers,
            'method': request.method,
            'reason': response.reason,
            'status_code': response.status_code,
            'url': request.url,
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
        self.message = message
        self.method = method
        self.fields = fields
        self.values = values


class PyCronofyPartialSuccessError(Exception):
    def __init__(self, message, batch_response):
        super(PyCronofyPartialSuccessError, self).__init__(message)
        self.message = message
        self.batch_response = batch_response
