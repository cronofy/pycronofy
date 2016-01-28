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

def set_debug(debug=False):
    settings.DEBUG = debug