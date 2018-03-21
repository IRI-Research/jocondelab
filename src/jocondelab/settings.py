# -*- coding: utf-8 -*-
#
# Copyright Institut de Recherche et d'Innovation © 2014
#
# contact@iri.centrepompidou.fr
#
# Ce code a été développé pour un premier usage dans JocondeLab, projet du 
# ministère de la culture et de la communication visant à expérimenter la
# recherche sémantique dans la base Joconde
# (http://jocondelab.iri-research.org/).
#
# Ce logiciel est régi par la licence CeCILL-C soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL-C telle que diffusée par le CEA, le CNRS et l'INRIA 
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant 
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
# pris connaissance de la licence CeCILL-C, et que vous en avez accepté les
# termes.
#
# Django settings for jocondelab project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

ugettext = lambda s: s

LANGUAGES = ( 
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
    ('it', ugettext('Italian')),
    ('es', ugettext('Spanish')),
    ('de', ugettext('German')),
    ('pt', ugettext('Portuguese')),
    ('ar', ugettext('Arabic')),
    ('ru', ugettext('Russian')),
    ('zh-cn', ugettext('Chinese')),
    ('ja', ugettext('Japanese')),
    ('ca', ugettext('Catalan')),
    ('eu', ugettext('Basque')),
    ('br', ugettext('Breton')),
    ('oc', ugettext('Occitan')),
)


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

#use etags
USE_ETAGS = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',    
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'jocondelab.urls'

AUTH_USER_MODEL = 'core.User'
INITIAL_CUSTOM_USER_MIGRATION = "0001_initial"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'jocondelab.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    'django.core.context_processors.request',
    "django.contrib.messages.context_processors.messages",    
    "jocondelab.context_processors.version"
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.admin',
    'haystack',
    'south',
    'mptt',
    'pipeline',
    'core',
    'jocondelab',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

WIKIPEDIA_URLS = {
    'fr': {
        'base_url': "http://fr.wikipedia.org",
        'page_url': "http://fr.wikipedia.org/wiki",
        'api_url': "http://fr.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://fr.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://fr.dbpedia.org",
        'dbpedia_uri' : "http://fr.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://fr.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': False,
        'disambiguation_cat' : u'Catégorie:Homonymie',
    },
    'en': {
        'base_url': "http://en.wikipedia.org",
        'page_url': "http://en.wikipedia.org/wiki",
        'api_url': "http://en.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://en.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://dbpedia.org",
        'dbpedia_uri' : "http://dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': False,
        'disambiguation_cat' : u'Category:Disambiguation pages',
    },
    'it': {
        'base_url': "http://it.wikipedia.org",
        'page_url': "http://it.wikipedia.org/wiki",
        'api_url': "http://it.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://it.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://it.dbpedia.org",
        'dbpedia_uri' : "http://it.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://it.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': True,
        'disambiguation_cat' : u'Categoria:Disambigua',
    },
    'de': {
        'base_url': "http://de.wikipedia.org",
        'page_url': "http://de.wikipedia.org/wiki",
        'api_url': "http://de.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://de.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://de.dbpedia.org",
        'dbpedia_uri' : "http://de.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://de.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': True,
        'disambiguation_cat' : u'Kategorie:Begriffsklärung',
    },
    'ja': {
        'base_url': "http://ja.wikipedia.org",
        'page_url': "http://ja.wikipedia.org/wiki",
        'api_url': "http://ja.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://ja.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://ja.dbpedia.org",
        'dbpedia_uri' : "http://ja.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://ja.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': False,
        'disambiguation_cat' : u'カテゴリ:同名の地名',
    },
}

JOCONDE_IMAGE_BASE_URL = "http://www2.culture.gouv.fr/Wave/image/joconde"
JOCONDE_NOTICE_BASE_URL = "http://www.culture.gouv.fr/public/mistral/joconde_fr?ACTION=CHERCHER&FIELD_98=REF&VALUE_98="
JOCONDE_TERM_TREE_MAX_CHILDREN = 50
JOCONDE_TERM_TREE_MAX_ROOT_NODE = 300 

TERM_LIST_PAGE_SIZE = 20
PAGINATOR_VISIBLE_RANGE = 5
# 24 hours DB_QUERY_CACHE_TIME
DB_QUERY_CACHE_TIME = 86400

CACHE_MIDDLEWARE_SECONDS = 600
HOME_CACHE_SECONDS = 30

#MAX number of term in case search term does not recognize a wikipedia label 
MAX_TERMS_QUERY = 200

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        'KEY_FUNCTION' : 'jocondelab.utils.make_key'
    },
}


BASE_CSS = ('jocondelab/css/smoothness/jquery-ui-1.10.3.custom.min.css', 'jocondelab/lib/jquery.tagit.css', 'jocondelab/css/front-common.css')

PIPELINE_CSS = {
    'front-base': {
        'source_filenames': BASE_CSS,
        'output_filename': 'jocondelab/css/front-base.min.css',
    },
    'front-credits': {
        'source_filenames': BASE_CSS + (
            'jocondelab/css/front-credits.css',
        ),
        'output_filename': 'jocondelab/css/front-credit.min.css',
    },
    'front-timeline': {
        'source_filenames': BASE_CSS + (
            'jocondelab/css/front-timeline.css',
        ),
        'output_filename': 'jocondelab/css/front-timeline.min.css',
    },
    'front-termlist': {
        'source_filenames': BASE_CSS + (
            'jocondelab/css/front-termlist.css',
        ),
        'output_filename': 'jocondelab/css/front-termlist.min.css',
    },
    'front-notice': {
        'source_filenames': BASE_CSS + (
            'jocondelab/lib/magnific-popup.css',
            'jocondelab/css/front-notice.css'
        ),
        'output_filename': 'jocondelab/css/front-notice.min.css',
    },
    'front-geo': {
        'source_filenames': BASE_CSS + (
            'jocondelab/lib/leaflet.css',
            'jocondelab/lib/L.Control.Zoomslider.css',
            'jocondelab/css/front-geo.css',
        ),
        'output_filename': 'jocondelab/css/front-geo.min.css',
    },
    'front-home': {
        'source_filenames': BASE_CSS + (
            'jocondelab/css/front-home.css',
         ),
        'output_filename': 'jocondelab/css/front-home.min.css',
    },
    'front-students': {
        'source_filenames': BASE_CSS + (
            'jocondelab/css/front-students.css',
         ),
        'output_filename': 'jocondelab/css/front-students.min.css',
    },
    'front-students-group': {
        'source_filenames': BASE_CSS + (
            'jocondelab/css/front-students.css',
         ),
        'output_filename': 'jocondelab/css/front-students-group.min.css',
    },
}


BASE_JS = (
    'jocondelab/lib/underscore-min.js',
    'jocondelab/lib/jquery.min.js' ,
    'jocondelab/lib/jquery-ui.min.js',
    'jocondelab/lib/jquery.ui.touch-punch.min.js',
    'jocondelab/lib/tag-it.min.js',
    'jocondelab/js/front-common.js',
)
BASE_JS_SEARCH = BASE_JS + (
    'jocondelab/js/front-search.js',
)

PIPELINE_JS = {
    'front-geo': {
        'source_filenames': BASE_JS + (
            'jocondelab/lib/leaflet.js',
            'jocondelab/lib/L.Control.Zoomslider.js',
            'jocondelab/lib/oms.min.js',
            'jocondelab/js/front-geo.js',
        ),
        'output_filename': 'jocondelab/js/front-geo.min.js',
    },
    'front-home': {
        'source_filenames': BASE_JS_SEARCH + (
          'jocondelab/js/front-home.js',
        ),
        'output_filename': 'jocondelab/js/front-home.min.js',
    },
    'front-notice': {
        'source_filenames': BASE_JS + (
          'jocondelab/lib/jquery.magnific-popup.min.js',
          'jocondelab/js/front-notice.js',
        ),
        'output_filename': 'jocondelab/js/front-notice.min.js',
    },
    'front-search': {
        'source_filenames': BASE_JS_SEARCH,
        'output_filename': 'jocondelab/js/front-search.min.js',
    },
    'front-students-group': {
        'source_filenames': BASE_JS + (
          'jocondelab/lib/videojs/video.js',
        ),
        'output_filename': 'jocondelab/js/front-students-group.min.js',
    },
    'front-students': {
        'source_filenames': BASE_JS + (
          'jocondelab/lib/videojs/video.js',
        ),
        'output_filename': 'jocondelab/js/front-students.min.js',
    },
    'front-termlist': {
        'source_filenames': BASE_JS + (
          'jocondelab/js/front-termlist.js',
        ),
        'output_filename': 'jocondelab/js/front-termlist.min.js',
    },
    'front-timeline': {
        'source_filenames': BASE_JS + (
          'jocondelab/lib/jquery.mousewheel.js',
          'jocondelab/lib/hammer.min.js',
          'jocondelab/js/front-timeline.js',
        ),
        'output_filename': 'jocondelab/js/front-timeline.min.js',
    },
}

PIPELINE_CSS_COMPRESSOR = "pipeline.compressors.yuglify.YuglifyCompressor"
PIPELINE_JS_COMPRESSOR = "pipeline.compressors.yuglify.YuglifyCompressor"


from config import *  # @UnusedWildImport

if not "SRC_BASE_URL" in locals():
    SRC_BASE_URL = BASE_URL + __name__.split('.')[0] + '/'     
if not "LOGIN_URL" in locals():
    LOGIN_URL = SRC_BASE_URL + 'auth/login/'

