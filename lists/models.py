from django.db import models
from django.urls import reverse

from superlists import settings


class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="ownership")
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="shared_with")

    @property
    def name(self):
        return self.item_set.first().text

    def get_absolute_url(self):
        return reverse("view_list", args=[self.id])

    @staticmethod
    def create_new(first_item_text, owner=None):
        list_ = List.objects.create(owner=owner)
        Item.objects.create(text=first_item_text, list=list_)
        return list_


class Item(models.Model):
    text = models.TextField(default="")
    list = models.ForeignKey(List, default=None)

    class Meta:
        unique_together = ("list", "text")
        ordering = ['pk']

    def __str__(self):
        return self.text
