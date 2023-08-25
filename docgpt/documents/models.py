from django.db import models
from django.contrib.auth.models import User
from categories.models import Category


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=50, null=False)
    file_hash = models.CharField(max_length=256)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=False)
    upload = models.FileField(
        upload_to="", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
