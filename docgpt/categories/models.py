from django.db import models


class Category(models.Model):
    category = models.CharField(
        max_length=100, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
