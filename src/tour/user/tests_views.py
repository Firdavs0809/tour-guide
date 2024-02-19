from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserTestCase(APITestCase):
    def test_registration(self):
        data = {
            'first_name': 'Test',
            'phone_number': "+998878493984",
            'password': 'anypassword'
        }
        response = self.client.post(reverse('api:auth-registration'), data=data, format='json')

        self.assertEquals(response.status_code, 200)

    def test_activation(self, ):
        data = {
            'phone_number': '+998878493984',
            'code': '787678'
        }
        response = self.client.post(reverse('api:auth-register-activation'), data=data)

        # self.assertEquals(response.status_code, 200)

    def test_incorrect_activation(self, ):
        data = {
            'phone_number': '+998878493984',
            'code': '787678'
        }
        response = self.client.post(reverse('api:auth-register-activation'), data=data)

        # self.assertEquals(response.status_code, 200)

    def test_sign_in(self, ):
        data = {
            'phone_number': '+998878493984',
            'password': 'anypassword'
        }
        response = self.client.post(reverse('api:auth-login'), data=data)

        # self.assertEquals(response.status_code, 200)

    def test_phone_number_duplication(self):
        data = {
            'first_name': 'TestDuplication',
            'phone_number': "+998878493984",
            'password': 'anypassword1'
        }
        response = self.client.post(reverse('api:auth-registration'), data=data, format='json')

        # self.assertEquals(response.status_code, 400)

    def test_incorrect_login(self):
        data = {
            'phone_number': '+998878493984',
            'password': 'anypassword'
        }
        response = self.client.post(reverse('api:auth-login'), data=data)

        # self.assertEquals(response.status_code, 200)
