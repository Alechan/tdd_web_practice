import uuid

from django.contrib import auth
from django.db import models
from django.urls import reverse

auth.signals.user_logged_in.disconnect(auth.models.update_last_login)


class User(models.Model):
    email = models.EmailField(primary_key=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    is_anonymous = False
    is_authenticated = True

    def __str__(self):
        return f"{self.email}"


class Token(models.Model):

    email = models.EmailField()
    uid   = models.CharField(default=uuid.uuid4, max_length=40)

    @classmethod
    def from_email(cls, email, request):
        token = Token.objects.create(email=email)
        url = request.build_absolute_uri(
            reverse("login") + '?token=' + str(token.uid)
        )
        return url

    class Meta:
        unique_together = ('email', 'uid',)
