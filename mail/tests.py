from django.test import TestCase
from django.contrib.auth.models import User
from .models import Email
from django.urls import reverse

class EmailModelTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_email_creation(self):
        # Test that an email can be created correctly
        email_obj = Email.objects.create(
            user=self.user,
            from_email='sender@example.com',
            to='recipient@example.com',
            subject='Test Subject',
            body_plain='Test Body'
        )
        self.assertEqual(email_obj.user, self.user)
        self.assertEqual(email_obj.subject, 'Test Subject')
        self.assertEqual(email_obj.email_type, 1) # Checks the default value

class InboxViewTest(TestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        
    def test_inbox_view_success(self):
        # Use reverse() to get the URL by its name
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail/inbox.html')

    def test_inbox_view_redirects_unauthenticated_user(self):
        # Log out the client to test the @login_required decorator
        self.client.logout()
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 302) # Expect a redirect
        self.assertRedirects(response, '/users/login/?next=/mail/inbox/')

    def test_inbox_view_shows_emails(self):
        # Create an email for the user
        Email.objects.create(
            user=self.user,
        )
        