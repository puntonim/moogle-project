"""
Magpie settings

First set an environment variable like:
    MAGPIE_SETTINGS_MODULE=magpie.settings.local
Then you can import settings in any module, like:
    $ from magpie.settings import settings
"""

from os.path import join, normpath, dirname
from models import Provider


BASE_DIR = normpath(dirname(dirname(dirname(__file__))))

DATABASE = {
    'ENGINE': 'sqlite:///',
    'NAME': normpath(join(BASE_DIR, 'magpie.db')),
}

# Dropbox settings.
DROPBOX_MAX_FILE_SIZE = 10*1024*1024  # 10 MB in bytes
DROPBOX_TEMP_STORAGE_PATH = normpath(join(BASE_DIR, '_tmp', 'dropbox'))
DROPBOX_FILE_EXT_FILTER = ['txt', 'doc', 'docx', 'pdf']  # lowercase!

# Redis connection.
REDIS = {
    'UNIX_SOCKET': {
        'PATH': '/tmp/redis.sock',
    }
}

# Solr connection.
SOLR_URL = 'http://127.0.0.1:8983/solr'
CORE_NAMES = {
    Provider.NAME_TWITTER: 'twitter',
    Provider.NAME_FACEBOOK: 'facebook',
    Provider.NAME_DROPBOX: 'dropbox'
}