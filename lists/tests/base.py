from bs4 import BeautifulSoup
from django.test import TestCase


class DjangoTestCase(TestCase):
    @staticmethod
    def get_DOM_for_response(response):
        html = response.content
        bs = BeautifulSoup(html, "html5lib")
        return bs

    def assertFormContainsValidInput(self, form, input_id, input_type):
        label = form.findChild("label")
        self.assertIsNotNone(label)
        self.assertEqual(label.get("for"), input_id)
        self.assertGreater(len(label.text), 0)
        input_email = form.findChild("input", {"id": input_id})
        self.assertIsNotNone(input_email)
        self.assertEqual(input_email.get("type"), input_type)
        self.assertEqual(input_email.get("placeholder"), "your-friend@example.com")

    def assertFormContainsValidSubmitButton(self, form):
        input_submit = form.findChild("input", {"type": "submit"})
        self.assertIsNotNone(input_submit)
        self.assertGreater(len(input_submit.get("value")), 0)

    def assertFormContainsValidCSRFToken(self, form):
        input_csrf = form.findChild("input", {"name": "csrfmiddlewaretoken"})
        self.assertIsNotNone(input_csrf)
        self.assertEqual(input_csrf.get("type"), "hidden")
        self.assertGreater(len(input_csrf.get("value")), 20)
