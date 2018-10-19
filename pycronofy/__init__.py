from pycronofy.client import Client  # noqa: F401
from pycronofy import settings
__version__ = '1.1.7'
__name__ = 'PyCronofy'

"""
Python library wrapping Cronofy:

More info available at:

https://www.cronofy.com/developers/
https://github.com/venuebook/pycronofy
"""


def set_request_hook(func):
    """Sets a function to execute on requests made by pycronofy
    via the requests model.

    Accepts arguments (response, *args, **kwargs).

    :param function func: Function to execute on request.
    """
    settings.REQUEST_HOOK = {'response': func} if func else {}
