from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import Token

EMAIL = 'a@b.com'

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_is_valid_with_email_only(self):
        user = User(email=EMAIL)
        try:
            user.full_clean()  # should not raise
        except ValidationError:
            self.fail("An email should be enough to create a User.")

    def test_email_is_primary_key(self):
        user = User(email=EMAIL)
        self.assertEqual(user.pk, EMAIL)

    def test_no_problem_with_auth_login(self):
        user = User.objects.create(email=EMAIL)
        user.backend = ''
        request = self.client.request().wsgi_request
        auth.login(request, user)  # should not raise


class TokenModelTest(TestCase):
    def test_links_user_with_auto_generated_uid(self):
        token1 = Token.objects.create(email=EMAIL)
        token2 = Token.objects.create(email=EMAIL)
        self.assertNotEqual(token1.uid, token2.uid)

    def test_token_creation_from_email_returns_valid_url(self):
        request = self.client.request().wsgi_request
        url = Token.from_email(EMAIL, request)
        self.validate_test_url(url)

    def validate_test_url(self, test_url):
        validator = URLValidator()
        self.assertIn("testserver", test_url)
        url = test_url.replace("testserver", "testserver.com")
        validator(url)
