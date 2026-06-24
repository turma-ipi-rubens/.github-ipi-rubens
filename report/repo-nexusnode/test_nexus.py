from rest_framework.test import APITestCase

class BoilerplateTest(APITestCase):
    def test_status_base(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
