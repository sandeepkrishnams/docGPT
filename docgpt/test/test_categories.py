from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from categories.models import Category
from django.contrib.auth.models import User


class CategoryListViewTests(APITestCase):
    def setUp(self):
        self.category_list_url = reverse('category-list')
        self.superuser = User.objects.create_superuser(
            username='superuser', password='superuser')
        self.user = User.objects.create_user(
            username='testuser@gmail.com', password='testpassword')

    def test_create_category_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        category_data = {
            "category": "Test Category"
        }
        response = self.client.post(
            self.category_list_url, category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('response', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data.get('message'),
                         'Registration successful')

    def test_create_category_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        category_data = {
            "category": "Test Category"
        }
        response = self.client.post(
            self.category_list_url, category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_categories_as_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_category_by_id_as_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        category = Category.objects.create(category="Test Category")
        response = self.client.get(
            reverse('category-delete', args=[category.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category'], 'Test Category')

    def test_get_category_by_invalid_id_as_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('category-delete', args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Category not found')

    def test_delete_category_as_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        category = Category.objects.create(category="Test Category")
        response = self.client.delete(
            reverse('category-delete', args=[category.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, f"Category '{category.category}' Deleted.")

    def test_delete_category_as_regular_user(self):
        self.client.force_authenticate(user=self.user)
        category = Category.objects.create(category="Test Category")
        response = self.client.delete(
            reverse('category-delete', args=[category.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
