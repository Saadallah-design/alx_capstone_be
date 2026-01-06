from pathlib import Path
from dotenv import load_dotenv
import os



load_dotenv()
# env = os.environ.Env()
# os.environ.Env.read_env(os.path.join(BASE_DIR, 'carRentalConfig/.env'))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

# CORS Settings
DEBUG = os.getenv('DEBUG') == 'True'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# local hosts for development
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# CORS settings
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    CORS_ALLOW_CREDENTIALS = True   

# Add Render.com host in production
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres', # Required for ExclusionConstraint
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'users',
    'core',
    'branches',
    'vehicles',
    'rentals',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist', # this one is optional: for token blacklisting
    'django_filters',
    'drf_spectacular',
    'django_extensions',
    'corsheaders',
    'payments'
    
   
    # 'sslserver', # For HTTPS dev server
]

# Custom authentication backends
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameBackend',  # Allow email or username login
    'django.contrib.auth.backends.ModelBackend',  # Fallback to default
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'carRentalConfig.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'carRentalConfig.wsgi.application'

    # settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',
        'user': '10000/day'
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


# Database configuration
import dj_database_url

DATABASE_URL = os.getenv('DATABASE_URL')

# Support Render deployment while allowing local environment variables
if DATABASE_URL and not DATABASE_URL.startswith('postgres://user:password'):
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB_NAME'),
            'USER': os.getenv('POSTGRES_DB_USER'),
            'PASSWORD': os.getenv('POSTGRES_DB_PASSWORD'),
            'HOST': os.getenv('POSTGRES_DB_HOST'),
            'PORT': os.getenv('POSTGRES_DB_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (User uploads)
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# # Whitenoise configuration for serving static files
# if not DEBUG:
#     STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ALX Car Rental API',
    'DESCRIPTION': 'Comprehensive API for the ALX Capstone Car Rental Platform. Supports dual roles (Agencies/Customers), location tracking, and real-time booking management.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

     

# Stripe
STRIPE_TEST_SECRET_KEY = os.getenv('STRIPE_TEST_SECRET_KEY')  # Your test secret key
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET') 

SITE_URL = os.getenv('SITE_URL', 'http://localhost:5173')


#Cloudinary Setting
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Storage configuration - Use basic StaticFilesStorage to avoid font file issues
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Legacy settings for django-cloudinary-storage compatibility
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Still needed for local reference and URL generation
MEDIA_URL = '/media/'