from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-r@b-w_@w@p!f0345q5wn4bv8st+%5(rxyz4jba62w#u=r(@s00')
DEBUG = False

AUTH_USER_MODEL = 'accounts.User'
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework',
    'django_filters',
    'axes',
    "ckeditor",
    "ckeditor_uploader", 
    'accounts',
    'admin_management',
    'ecomapp',
    'products',
    'orders',
    'shops',
    'haatbazar',
    'payments',
    'mathfilters',
    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Production Static serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware', 
]

if DEBUG:
    MIDDLEWARE.insert(5, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'single_E_comerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ecomapp.context_processors.global_site_settings',
                'shops.context_processors.shop_global_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'single_E_comerce.wsgi.application'

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]

# Static files (CSS, JavaScript, Images) Setup
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static", 
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Django Modern STORAGES Setup for WhiteNoise (Fixes MIME/404 Issue)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
WHITENOISE_MANIFEST_STRICT = False

# Media dynamic files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CKEditor settings
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication', 
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=600),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

# Axes Configuration
AXES_FAILURE_LIMIT = 10 
AXES_COOLOFF_TIME = 1 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SSLCommerz settings
SSLCOMMERZ_STORE_ID = os.getenv('SSLCOMMERZ_STORE_ID')
SSLCOMMERZ_STORE_PASSWORD = os.getenv('SSLCOMMERZ_STORE_PASSWORD')
SSLCOMMERZ_API_URL = os.getenv('SSLCOMMERZ_API_URL')
SSLCOMMERZ_VALIDATION_API = os.getenv('SSLCOMMERZ_VALIDATION_API')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'imrabbihasan@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'uvvrotdsqwbyhzko')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Session settings
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# CSRF & Security Setup
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 
    'http://127.0.0.1:8000',
    'https://*.up.railway.app',
    'https://*.railway.app',
    'https://permissible-sloshy-maribel.ngrok-free.dev',
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_DOMAIN = None 
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True