from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tour.user'

    def ready(self):
        import tour.user.signals
