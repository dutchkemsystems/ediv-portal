import os

# Only import celery if broker is configured
if os.environ.get("CELERY_BROKER_URL"):
    from .celery import app as celery_app  # noqa: F401

    __all__ = ("celery_app",)
else:
    __all__ = ()
