from os.path import join, normpath
from .base import BASE_DIR


# Set the log folder: a folder named 'log' in the root folder of the project
LOG_FOLDER = normpath(join(BASE_DIR, 'magpie', 'logs'))

# The log settings dictionary
LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'basic': {
            'format': '%(asctime)s %(levelname)s - %(message)s'
        },
        'advanced': {
            'format': '%(asctime)s %(levelname)s %(name)s %(filename)s@%(lineno)d - %(message)s'
        },
    },

    'handlers': {
        'magpie_hl': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': normpath(join(LOG_FOLDER, 'magpie.log')),
            'mode': 'a',
            'maxBytes': 1048576*5,  # max 5 Mbyte
            'backupCount': 0,  # max 1 file
            'formatter': 'advanced',
        },
        'facebook_hl': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': normpath(join(LOG_FOLDER, 'facebook.log')),
            'mode': 'a',
            'maxBytes': 1048576*5,  # max 5 Mbyte
            'backupCount': 0,  # max 1 file
            'formatter': 'advanced',
        },
    },

    'loggers': {
        '': {
            'handlers': ['magpie_hl'],
            'level': 'DEBUG',
        },
        'facebook': {
            'handlers': ['facebook_hl'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
