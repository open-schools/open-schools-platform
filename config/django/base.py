"""
Django settings for open_schools_platform project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from config.env import env, environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = environ.Path(__file__) - 3

env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=ug_ucl@yi6^mrcjyz%(u0%&g2adt#bz3@yos%#@*t#t!ypx=a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
APPEND_SLASH = False
ALLOWED_HOSTS = ['*']

# Application definition

LOCAL_APPS = [
    'open_schools_platform.common.apps.CommonConfig',
    'open_schools_platform.tasks.apps.TasksConfig',
    'open_schools_platform.api.apps.ApiConfig',
    'open_schools_platform.user_management.users.apps.UsersConfig',
    'open_schools_platform.user_management.authentication.apps.AuthenticationConfig',
    'open_schools_platform.organization_management.organizations.apps.OrganizationsConfig',
    'open_schools_platform.organization_management.employees.apps.EmployeesConfig',
    'open_schools_platform.errors.apps.ErrorsConfig',
    'open_schools_platform.parent_management.families.apps.FamiliesConfig',
    'open_schools_platform.parent_management.parents.apps.ParentsConfig',
    'open_schools_platform.student_management.students.apps.StudentConfig',
    'open_schools_platform.query_management.queries.apps.QueriesConfig',
    'open_schools_platform.organization_management.circles.apps.CirclesConfig',
    'open_schools_platform.photo_management.photos.apps.PhotosConfig',
    'open_schools_platform.history_management.apps.HistoryConfig',
    'open_schools_platform.ticket_management.tickets.apps.TicketsConfig',
    'open_schools_platform.organization_management.teachers.apps.TeachersConfig',
    'open_schools_platform.testing.apps.TestingConfig',
    'open_schools_platform.sms.apps.SmsConfig'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_gis',
    'django.contrib.gis',
    'django_celery_results',
    'django_celery_beat',
    'django_filters',
    'leaflet',
    'corsheaders',
    'django_extensions',
    'rest_framework_jwt',
    'phonenumber_field',
    'rules.apps.AutodiscoverRulesConfig',
    'storages',
    'safedelete',
    'import_export',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

LOCAL_MIDDLEWARES = [
    'open_schools_platform.middleware.LastLoginIP.LastLoginIPMiddleware',
    'open_schools_platform.middleware.RemoveTrailingSlash.RemoveTrailingSlashMiddleware',
]

THIRD_PARTY_MIDDLEWARES = [
    'simple_history.middleware.HistoryRequestMiddleware',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    *THIRD_PARTY_MIDDLEWARES,
    *LOCAL_MIDDLEWARES
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///open_schools_platform'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

if env('GITHUB_WORKFLOW', default=None):
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'github_actions',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = env('LOCALE_LANGUAGE', default='en')

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'config', 'locale')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

if env("STATIC_ROOT", default=None):
    STATIC_ROOT = env("STATIC_ROOT")
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'open_schools_platform.api.exception_handlers.drf_default_with_modifications_exception_handler',  # noqa: E501
    'DEFAULT_FILTER_BACKENDS': (
        'open_schools_platform.common.filters.CustomDjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'login': env("LOGIN_RATE_LIMIT", default="10/minute"),
        'token_creation': env("TOKEN_CREATION_RATE_LIMIT", default="10/minute")
    }
}

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

from config.settings.cors import *  # noqa
from config.settings.jwt import *  # noqa
from config.settings.sessions import *  # noqa
from config.settings.celery import *  # noqa
from config.settings.sentry import *  # noqa
from config.settings.geo_django import *  # noqa
from config.settings.file_storages import *  # noqa
from config.settings.email import *  # noqa

ADMIN_PANEL_ENABLED = env.bool('ADMIN_PANEL_ENABLED', default=True)

from config.settings.debug_toolbar.settings import *  # noqa
from config.settings.debug_toolbar.setup import DebugToolbarSetup  # noqa

INSTALLED_APPS, MIDDLEWARE = DebugToolbarSetup.do_settings(INSTALLED_APPS, MIDDLEWARE)

from config.settings.swagger.settings import *  # noqa
from config.settings.swagger.setup import SwaggerSetup  # noqa

INSTALLED_APPS, MIDDLEWARE = SwaggerSetup.do_settings(INSTALLED_APPS, MIDDLEWARE)
