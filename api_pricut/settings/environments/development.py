from .base import *


# Application definition
INSTALLED_APPS.extend(["django_extensions"])


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    config("BACKEND_HOST", cast=str),
    config("FRONTEND_HOST", cast=str),
    config("FRONTEND_HOST_LOCAL", cast=str),
]

CSRF_TRUSTED_ORIGINS = [
    config("BACKEND_URL", cast=str),
    config("FRONTEND_URL", cast=str),
    config("FRONTEND_LOCAL_URL", cast=str),
]

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True


# CORS settings
CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = [
    config("FRONTEND_URL", cast=str),
    config("FRONTEND_LOCAL_URL", cast=str),
]


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = Path.joinpath(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# SMTP settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


# API documentation settings

SPECTACULAR_SETTINGS["SERVERS"] = [
    {
        "url": config("BACKEND_URL", cast=str),
        "description": "Development server" if DEBUG else "Production server",
    }
]
