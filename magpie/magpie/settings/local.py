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

# Test bearertoken_ids
TEST_BEARERTOKEN_IDS = [1000000, 1000001, 1000002]

# Solr connection.
SOLR_URL = 'http://192.168.1.76:8983/solr'

# Logging
from logging.config import dictConfig
from .logging.local import LOGGING_DICT
dictConfig(LOGGING_DICT)