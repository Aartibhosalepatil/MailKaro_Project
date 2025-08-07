from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@receiver(user_logged_in)
def send_login_notification(sender, request, user, **kwargs):
    """
    Sends a login notification email to the user after they successfully log in.
    """
    # This print statement will appear in the console if the signal is fired.
    print(f"DEBUG: Signal received for user: {user.username}. Attempting to send login notification email.")
    
    subject = 'Successful Login to MailKaro'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    # Create a simple email template (or render an HTML one)
    html_message = render_to_string('mail/login_notification_email.html', {'user': user})
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Login notification email sent successfully to {user.email}")
    except Exception as e:
        print(f"Failed to send login notification email to {user.email}. Error: {e}")