"""
Django settings for starter project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=#3l43&4ba1d0y(0-*^xxrys-dy^28s9ni_+6c^y)--l38-^^)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',
    'wb',
    'ozon',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'starter.urls'

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

WSGI_APPLICATION = 'starter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        'HOST': 'db',
        'PORT': '5432',
        'USER': 'seeski',
        'PASSWORD': 'Starter_Expert%060723',
        'NAME': 'starterdb',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = '/static/'
STATIC_URL = '/static/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = 'redis://redis:6379'

LOGIN_REDIRECT_URL = 'staff_home'

CSRF_TRUSTED_ORIGINS = [
    'https://starter.expert',
    'http://starter.expert',
    'https://217.74.250.25',
    'http://217.74.250.25',
    'https://localhost',
    'http://localhost',
    'https://127.0.0.1',
    'http://127.0.0.1',
    'https://192.168.0.2',
    'http://192.168.0.2',
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = 20480

IMPERSONATE = "chrome110"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'classic_formater': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "classic_formater",
        },
        "ozon_file_output": {
            "class": "logging.FileHandler",
            "filename": "./output_indexer.log",
            "formatter": 'classic_formater',
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "ozon_indexer": {
            "handlers": ["ozon_file_output", "console"],
            "level": "DEBUG",
        }
    },
}

ONLY_PROXY = False

PROXIES = [
    #{'https': 'socks5://SSZ9fn:vXbCdciP0x@185.181.246.191:1051'},
    #{'https': 'socks5://SSZ9fn:vXbCdciP0x@188.130.143.247:1051'},
    #{'https': 'socks5://SSZ9fn:vXbCdciP0x@46.8.110.195:1051'},
    #{'https': 'socks5://SSZ9fn:vXbCdciP0x@109.248.54.183:1051'},
    #{'https': 'socks5://SSZ9fn:vXbCdciP0x@95.182.125.71:1051'},
]
