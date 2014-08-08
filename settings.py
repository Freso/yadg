# Django settings for whatdesc project.
import secret

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Slack', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'E:/temp/what/bla-js.sql',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'E:/temp/what/public_static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
# ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'E:/temp/what/whatdesc/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = secret.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'E:/temp/what/whatdesc/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "djcelery",
    'descgen',
    'djangorestframework',
    'codemirror',
    'contact',
    'captcha',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'scraper': {
            'format': '[%(asctime)s: %(levelname)s/%(name)s] %(message)s [%(instance)s]'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'scraper_console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter':'scraper'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'descgen.scraper': {
            'handlers': ['scraper_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

#email settings
EMAIL_HOST = '***REMOVED***'
EMAIL_HOST_USER = secret.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = secret.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = True
SERVER_EMAIL = '***REMOVED***'


#add celery
import djcelery
djcelery.setup_loader()

#celery config
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = secret.BROKER_USER
BROKER_PASSWORD = secret.BROKER_PASSWORD
BROKER_VHOST = "/"
CELERY_RESULT_BACKEND = 'database'
#CELERY_RESULT_DBURI = "sqlite:///celerydb.sqlite"
CELERY_TASK_RESULT_EXPIRES = 3600
#make sure the task is available in the database
CELERY_TRACK_STARTED = True


#add context processors
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request", #make request.path available in templates
)

#configure session framework
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 31536000 # 1 year in seconds
SESSION_FILE_PATH = 'E:/temp/what/'
SESSION_COOKIE_HTTPONLY = False # make sure cookie is sent with ajax calls

#set a custum csrf_failure view
CSRF_FAILURE_VIEW = "descgen.views.misc.csrf_failure"

CODEMIRROR_PATH = STATIC_URL + r"js/codemirror"

#recaptcha settings
RECAPTCHA_PUBLIC_KEY = secret.RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = secret.RECAPTCHA_PRIVATE_KEY
RECAPTCHA_USE_SSL = True

#contact form settings
CONTACT_RECIPIENTS = map(lambda x: x[1], ADMINS)

#config for auth
LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

#from 1.6 onward used instead of TransactionMiddleware
ATOMIC_REQUESTS = True