from django.conf import settings


def global_settings(request):
    return {
        "client_id": settings.CLIENT_ID,
    }
