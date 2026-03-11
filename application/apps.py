from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    """
    Configuration class for the 'application' app in a Django project.

    This class is used to configure the behavior and settings of the 'application' app.

    Attributes:
        default_auto_field (str): Specifies the default field type for automatically
            added primary keys in models. Set to 'BigAutoField' for 64-bit integers.
        name (str): The full Python path to the app. This is used by Django to locate
            and identify the app within the project.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "application"

