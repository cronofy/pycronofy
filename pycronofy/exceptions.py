class PyCronofyValidationError(Exception):
    def __init__(self, message, method, fields):
        super(PyCronofyValidationError, self).__init__(message)
        self.method = method
        self.fields = fields

class PyCronofyDateTimeError(Exception):
    def __init__(self, message, argument):
        """
        :param string message: Exception message.
        :param object argument: Value passed into get_iso8601_string.
        """
        super(PyCronofyDateTimeError, self).__init__(message)
        self.argument = argument