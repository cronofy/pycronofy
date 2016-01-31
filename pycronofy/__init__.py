from .client import Client
import settings
__version__ = '0.0.0'
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
    if func:
        settings.REQUEST_HOOK = {'response':func}
    else:
        settings.REQUEST_HOOK = {}