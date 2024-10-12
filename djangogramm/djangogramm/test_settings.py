from djangogramm.settings import *


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'EMAIL_AUTHENTICATION': True,
        'SCOPE': [
            'profile',
            'email'
        ],
        'APP': {
            'client_id': "my_client_id",
            'secret': "my_secret",
            'key': ''
        },
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'github': {
        'EMAIL_AUTHENTICATION': True,
        'SCOPE': [
            'user',
            'email'
        ],
        'APP': {
            'client_id': "my_client_id",
            'secret': "my_secret",
            'key': ''
        },
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
