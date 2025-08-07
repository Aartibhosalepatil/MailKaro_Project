# from django.apps import AppConfig

# from django.contrib.auth.apps import AuthConfig


# class MailConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'mail'
#     def ready(self):
#         import mail.signals
    




# class CustomAuthConfig(AuthConfig):
#     verbose_name = "🔒 User Management"

from django.apps import AppConfig

class MailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mail'
    def ready(self):
        print("DEBUG: mail.apps.MailConfig.ready() is being called. Importing signals.")
        import mail.signals

