from telnetlib import STATUS
from django.test import TestCase

# Create your tests here.


class TestApi(TestCase):
    def test_api_get(self):
        res= self.client.get('/api/')
        self.assertEqual(res.status_code,200)
        
    def test_api_post(self):
        url = '/api/'
        res = self.client.post(url)
        self.assertEqual(res.status_code,200)