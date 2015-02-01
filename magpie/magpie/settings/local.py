"""Development settings and globals."""

# Extend base settings
from .base import *

# Redis
REDIS = {
    'TCP_SOCKET': {
        #'HOST': '192.168.1.77',
        'HOST': '10.211.55.5',
        'PORT': 6379,
        'DB': 0,
    }
}

# Solr connection.
#SOLR_URL = 'http://192.168.1.76:8983/solr'
SOLR_URL = 'http://10.211.55.5:8983/solr'

# Logging
from logging.config import dictConfig
from .logging.local import LOGGING_DICT
dictConfig(LOGGING_DICT)