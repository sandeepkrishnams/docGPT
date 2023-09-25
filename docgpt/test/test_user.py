from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from rest_framework.utils.serializer_helpers import ReturnList


class UserSignupTests(APITestCase):
    def setUp(self):
        self.registration_url = reverse('signup')
        self.test_user_data = {
            'username': 'testuser@gmail.com',
            'password': 'testpassword',
            'first_name': 'test',
            'last_name': 'user',
        }

    def test_valid_signup(self):
        valid_response = self.client.post(
            self.registration_url, self.test_user_data, format='json')
        self.assertEqual(valid_response.status_code, status.HTTP_201_CREATED)

    def test_invalid_data(self):
        invalid_user_data = self.test_user_data.copy()
        invalid_user_data.pop('username')
        invalid_user_data.pop('password')
        invalid_response = self.client.post(
            self.registration_url, invalid_user_data, format='json')

        self.assertEqual(invalid_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            invalid_response.data['username'][0], "username address is required")
        self.assertEqual(
            invalid_response.data['password'][0], "Password is required")

    def test_invalid_username(self):
        invalid_user_data = self.test_user_data.copy()
        invalid_user_data['username'] = 'invalid_email'
        invalid_response = self.client.post(
            self.registration_url, invalid_user_data, format='json')

        self.assertEqual(invalid_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_response.data,
                         ["Username must be a valid email address."])

    def test_existing_user(self):
        User.objects.create_user(
            username='testuser@gmail.com', password='testpassword')
        valid_response = self.client.post(
            self.registration_url, self.test_user_data, format='json')

        self.assertEqual(valid_response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            valid_response.data['username'][0], "A user with that username already exists.")


class UserLoginTests(APITestCase):
    def setUp(self):
        self.login_url = reverse('token_obtain_pair')
        self.user = User.objects.create_user(
            username='testuser@gmail.com', password='testpassword')

    def test_valid_login(self):
        login_credentials = {
            'username': 'testuser@gmail.com',
            'password': 'testpassword'
        }
        response = self.client.post(
            self.login_url, login_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("refresh" in response.data)
        self.assertTrue("access" in response.data)

    def test_invalid_login(self):
        login_credentials = {
            'username': 'testuser@gmail.com',
            'password': 'invalid_password'
        }
        response = self.client.post(
            self.login_url, login_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {
                         "detail": "No active account found with the given credentials"})

    def test_no_login_credentials(self):
        login_credentials = {}
        response = self.client.post(
            self.login_url, login_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'username': [
                         'This field is required.'], 'password': ['This field is required.']})


class UserProfileTests(APITestCase):
    def setUp(self):
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            username='testuser@gmail.com', password='testpassword', first_name='test', last_name='user')
        self.super_user = User.objects.create_superuser(
            username='superuser', password='superuser')

    def test_user_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)
        self.assertIn('is_active', response.data)
        self.assertEqual(response.data.get('username'), 'testuser@gmail.com')
        self.assertEqual(response.data.get('first_name'), 'test')
        self.assertEqual(response.data.get('last_name'), 'user')
        self.assertEqual(response.data.get('is_active'), True)

    def test_superuser_access_all_users(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(self.profile_url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_keys = ['total_pages',
                         'current_page', 'total_data_count', 'data']
        self.assertTrue(all(key in response.data for key in response_keys))
        self.assertIsInstance(response.data.get('data'), ReturnList)
        self.assertEqual(response.data.get('total_pages'), 1)
        self.assertEqual(response.data.get('current_page'), 1)
        self.assertEqual(response.data.get('total_data_count'), 1)

        data = response.data.get('data')[0]
        expected_keys = ['id', 'username', 'first_name',
                         'last_name', 'date_joined', 'last_login']
        self.assertTrue(all(key in data for key in expected_keys))
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], 'testuser@gmail.com')
        self.assertEqual(data['first_name'], 'test')
        self.assertEqual(data['last_name'], 'user')

    def test_superuser_error_with_invalid_user_id(self):
        self.client.force_authenticate(user=self.super_user)
        response = self.client.get(self.profile_url + '0')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data.get('message'), 'Invalid ID')

        response = self.client.get(self.profile_url + str(self.user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(key in response.data for key in [
                        'total_pages', 'current_page', 'total_data_count', 'data']))
        self.assertIsInstance(response.data.get('data'), ReturnList)
        self.assertEqual(response.data.get('total_pages'), 1)
        self.assertEqual(response.data.get('current_page'), 1)
        self.assertEqual(response.data.get('total_data_count'), 1)
        self.assertTrue(len(response.data.get('data')), 1)
        self.assertTrue(response.data.get('data')[0].get('id') == self.user.id)


class UserPasswordUpdateTests(APITestCase):
    def setUp(self):
        self.update_password_url = reverse('updatepassword')
        self.user = User.objects.create_user(
            username='testuser@gmail.com', password='testpassword')

    def test_user_can_update_password(self):
        self.client.force_authenticate(user=self.user)
        password_credentials = {
            "new_password": "password",
            "old_password": "testpassword"
        }

        response = self.client.put(
            self.update_password_url, password_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Success', response.data)

        password_credentials['old_password'] = 'wrongpassword'
        response = self.client.put(
            self.update_password_url, password_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

        del password_credentials['old_password']
        del password_credentials['new_password']
        response = self.client.put(
            self.update_password_url, password_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)
        self.assertIn('old_password', response.data)
        self.assertEqual(response.data.get('new_password'),
                         ["This field is required."])
        self.assertEqual(response.data.get('old_password'),
                         ["This field is required."])

    def test_unauthenticated_user_cannot_update_password(self):
        password_credentials = {
            "new_password": "password",
            "old_password": "testpassword"
        }

        response = self.client.put(
            self.update_password_url, password_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileUpdateTests(APITestCase):
    def setUp(self):
        self.profile_update_url = reverse('profile')
        self.user = User.objects.create_user(
            username='testuser@gmail.com', password='testpassword', first_name='test', last_name='user')

    def test_user_can_update_profile(self):
        self.client.force_authenticate(user=self.user)
        updates = {
            "first_name": 'test',
            "last_name": 'user'
        }
        response = self.client.put(
            self.profile_update_url, updates, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('message', response.data)

        expected_keys = ['first_name', 'last_name']
        response_data = response.data.get('response')
        self.assertTrue(all(key in response_data for key in expected_keys))
        self.assertEqual(response_data.get('first_name'), 'test')
        self.assertEqual(response_data.get('last_name'), 'user')
