from django.utils import timezone

from django.contrib.auth import get_user_model


def create_user(**params):
    is_superuser = params.pop("is_superuser", False)

    defaults = {
        "email": "user@example.com",
        "password": "testpass123",
    }
    defaults.update(params)

    if is_superuser:
        return get_user_model().objects.create_superuser(**defaults)

    return get_user_model().objects.create_user(**defaults)


def get_time_in_timezone():
    return timezone.localtime()


def get_time_in_utc():
    return timezone.now()
