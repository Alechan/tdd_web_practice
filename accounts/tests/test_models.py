from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts import models
from accounts.models import Token

EMAIL = 'a@b.com'
ANOTHER_EMAIL = 'c@d.com'

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
        token2 = Token.objects.create(email=ANOTHER_EMAIL)
        self.assertNotEqual(token1.uid, token2.uid)

    def test_token_creation_from_email_returns_valid_url(self):
        url = self.get_testserver_token_url(EMAIL)
        self.validate_testserver_url(url)

    def test_url_contains_token_uid(self):
        url = self.get_testserver_token_url(EMAIL)
        uid = Token.objects.first().uid
        self.assertIn(uid, url)

    def test_token_creation_creates_only_one_object(self):
        _ = self.get_testserver_token_url(EMAIL)
        all_tokens = Token.objects.all()
        self.assertEqual(1, len(all_tokens))
        token = all_tokens[0]
        self.assertEqual(EMAIL, token.email)

    def test_if_email_already_registered_return_its_token(self):
        _ = self.get_testserver_token_url(EMAIL)
        try:
            _ = self.get_testserver_token_url(EMAIL)
        except IntegrityError:
            self.fail("It shouldn't try to create a token for a pre-registered email.")


    def validate_testserver_url(self, test_url):
        validator = URLValidator()
        self.assertIn("testserver", test_url)
        url = test_url.replace("testserver", "testserver.com")
        try:
            validator(url)
        except ValidationError:
            self.fail("The url is not valid.")

    def get_testserver_token_url(self, email):
        request = self.client.request().wsgi_request
        url = models.get_uid_url_for_email(email, request)
        return url

