"""
Django settings for tutorial project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import json
import os
import os.path as op
import slugid
import math

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
if 'HIGLASS_SERVER_BASE_DIR' in os.environ:
    base_dir = os.environ['HIGLASS_SERVER_BASE_DIR']

    if op.exists(base_dir):
        BASE_DIR = base_dir
    else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if 'HIGLASS_CACHE_DIR' in os.environ:
    # cache uploaded files
    # useful when using a mounted media directory
    CACHE_DIR = os.environ['HIGLASS_CACHE_DIR']
else:
    CACHE_DIR = None


if 'MAX_BAM_TILE_WIDTH' in os.environ:
    MAX_BAM_TILE_WIDTH = int(os.environ['MAX_BAM_TILE_WIDTH'])
else:
    MAX_BAM_TILE_WIDTH = int(1e5)

local_settings_file_path = os.path.join(
    BASE_DIR, 'config.json'
)

# load config.json
try:
    with open(local_settings_file_path, 'r') as f:
        local_settings = json.load(f)
except IOError:
    local_settings = {}
except ValueError as e:
    error_msg = "Invalid config '{}': {}".format(local_settings_file_path, e)
    raise ImproperlyConfigured(error_msg)


def get_setting(name, default=None, settings=local_settings):
    """Get the local settings variable or return explicit exception"""
    if default is None:
        raise ImproperlyConfigured(
            "Missing default value for '{0}'".format(name)
        )

    # Try looking up setting in `config.json` first
    try:
        return settings[name]
    except KeyError:
        pass

    # If setting is not found try looking for an env var
    try:
        return os.environ[name]

    # If nothing is found return the default setting
    except KeyError:
        if default is not None:
            return default
        else:
            raise ImproperlyConfigured(
                "Missing setting for '{0}' setting".format(name)
            )


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_setting('SECRET_KEY', slugid.nice())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_setting('DEBUG', False)

ALLOWED_HOSTS = [
    '*',
]

if 'SITE_URL' in os.environ:
    ALLOWED_HOSTS += [os.environ['SITE_URL']]

# this specifies where uploaded files will be place
# (e.g. BASE_DIR/media/uplaods/file.x)
MEDIA_URL = 'media/'

if 'HIGLASS_MEDIA_ROOT' in os.environ:
    MEDIA_ROOT = os.environ['HIGLASS_MEDIA_ROOT']
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if 'HTTPFS_HTTP_DIR' in os.environ:
    HTTPFS_HTTP_DIR = os.environ['HTTPFS_HTTP_DIR']
else:
    HTTPFS_HTTP_DIR = os.path.join(MEDIA_ROOT, 'http')

if 'HTTPFS_HTTPS_DIR' in os.environ:
    HTTPFS_HTTPS_DIR = os.environ['HTTPFS_HTTPS_DIR']
else:
    HTTPFS_HTTPS_DIR = os.path.join(MEDIA_ROOT, 'https')

if 'HTTPFS_FTP_DIR' in os.environ:
    HTTPFS_FTP_DIR = os.environ['HTTPFS_FTP_DIR']
else:
    HTTPFS_FTP_DIR = os.path.join(MEDIA_ROOT, 'ftp')

THUMBNAILS_ROOT = os.path.join(MEDIA_ROOT, 'thumbnails')
AWS_BUCKET_MOUNT_POINT = os.path.join(MEDIA_ROOT, 'aws')
THUMBNAIL_RENDER_URL_BASE = '/app/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': get_setting('LOG_LEVEL_CONSOLE', 'WARNING'),
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': get_setting('LOG_LEVEL_FILE', 'WARNING'),
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'log/hgs.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': get_setting('LOG_LEVEL_DJANGO', 'WARNING'),
        },
        'fragments': {
            'handlers': ['file'],
            'level': get_setting('LOG_LEVEL_FRAGMENTS', 'WARNING'),
        },
        'tilesets': {
            'handlers': ['file'],
            'level': get_setting('LOG_LEVEL_TILESETS', 'WARNING'),
        },
    }
}

if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']

if 'REDIS_HOST' in os.environ and 'REDIS_PORT' in os.environ:
    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']
else:
    REDIS_HOST = None
    REDIS_PORT = None

# DEFAULT_FILE_STORAGE = 'tilesets.storage.HashedFilenameFileSystemStorage'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'tilesets.apps.TilesetsConfig',
    'fragments.app.FragmentsConfig',
    'rest_framework_swagger',
    'corsheaders',
    'guardian'
]

# We want to avoid loading into memory
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
)

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = False

CORS_ORIGIN_WHITELIST = [
    'http://134.174.140.208:9000'
]

# CORS_ALLOW_HEADERS = default_headers

ROOT_URLCONF = 'higlass_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'higlass_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
    'NAME':
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
}, {
    'NAME':
    'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME':
    'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME':
    'django.contrib.auth.password_validation.NumericPasswordValidator',
}]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

UPLOAD_ENABLED = get_setting('UPLOAD_ENABLED', True)
PUBLIC_UPLOAD_ENABLED = get_setting('PUBLIC_UPLOAD_ENABLED', True)

SNIPPET_MAT_MAX_OUT_DIM = get_setting('SNIPPET_MAT_MAX_OUT_DIM', math.inf)
SNIPPET_MAT_MAX_DATA_DIM = get_setting('SNIPPET_MAT_MAX_DATA_DIM', math.inf)
SNIPPET_IMG_MAX_OUT_DIM = get_setting('SNIPPET_IMG_MAX_OUT_DIM', math.inf)
SNIPPET_OSM_MAX_DATA_DIM = get_setting('SNIPPET_OSM_MAX_DATA_DIM', math.inf)
SNIPPET_IMT_MAX_DATA_DIM = get_setting('SNIPPET_IMT_MAX_DATA_DIM', math.inf)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/hgs-static/'
STATIC_ROOT = 'hgs-static/'

if 'APP_BASEPATH' in os.environ:
    # https://stackoverflow.com/questions/44987110/django-in-subdirectory-admin-site-is-not-working
    USE_X_FORWARDED_HOST = True
    FORCE_SCRIPT_NAME = os.environ['APP_BASEPATH']
    SESSION_COOKIE_PATH = os.environ['APP_BASEPATH']
    LOGIN_REDIRECT_URL = os.environ['APP_BASEPATH']
    LOGOUT_REDIRECT_URL = os.environ['APP_BASEPATH']

    STATIC_URL = op.join(os.environ['APP_BASEPATH'], 'hgs-static') + "/"

ADMIN_URL = r'^admin/'

# STATICFILES_DIRS = (
#    os.path.join(BASE_DIR, 'static'),
# )

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = ['--nocapture', '--nologcapture']
