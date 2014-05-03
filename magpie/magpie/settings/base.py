"""
Magpie settings

First set an environment variable like:
    MAGPIE_SETTINGS_MODULE=magpie.settings.local
Then you can import settings in any module, like:
    $ from magpie.settings import settings
"""

from os.path import join, normpath, dirname


BASE_DIR = normpath(dirname(dirname(dirname(__file__))))

DATABASE = {
    'ENGINE': 'sqlite:///',
    'NAME': normpath(join(BASE_DIR, 'magpie.db')),
}

# Logging
from .logging import LOGGING_DICT
from logging.config import dictConfig
dictConfig(LOGGING_DICT)

# Dropbox
DROPBOX_MAX_FILE_SIZE = 10*1024*1024  # 10 MB in bytes
DROPBOX_TEMP_REPO_PATH = normpath(join(BASE_DIR, '_tmp', 'dropbox'))
DROPBOX_FILE_EXT_FILTER = ['txt', 'doc', 'docx', 'pdf']  # lowercase!

# Redis
REDIS = {
    'UNIX_SOCKET': {
        'PATH': '/tmp/redis.sock',
    }
}