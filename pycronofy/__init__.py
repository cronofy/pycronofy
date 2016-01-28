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

def set_debug(debug):
    """Sets DEBUG mode.

    :param bool debug: Set debug to True or False.
    """
    settings.DEBUG = debug