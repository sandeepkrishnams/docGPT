from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category', 'created_at', 'updated_at']
        extra_kwargs = {
            'category': {'required': True},
            'id': {'required': True}
        }


class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']
        extra_kwargs = {
            'category': {'required': True},
        }
