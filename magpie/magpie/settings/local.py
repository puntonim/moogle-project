"""Development settings and globals."""

# Extend base settings
from .base import *

# Redis
REDIS = {
    'TCP_SOCKET': {
        'HOST': '192.168.1.77',
        'PORT': 6379,
        'DB': 0,
    }
}

# Logging
from logging.config import dictConfig
from .logging.local import LOGGING_DICT
dictConfig(LOGGING_DICT)