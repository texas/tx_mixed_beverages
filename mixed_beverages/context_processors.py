from django.conf import settings


def map_config(request):
    return {
        "STADIA_API_KEY": settings.STADIA_API_KEY,
    }
