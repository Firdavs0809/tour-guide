import json
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from tour.oauth2.models import Application
from tour.user.models import User, Temp
from django.contrib.auth.hashers import make_password


class UserRegisterTestCase(APITestCase):

    def setUp(self):
        self.application = Application.objects.create(authorization_grant_type='password', client_type='confidential')
        self.client_id = self.application.client_id
        self.client_secret = self.application.client_secret

        data = {
            'first_name': 'Test',
            'phone_number': "+998900000000",
            'password': 'anypassword'
        }
        self.client.post(reverse('api:auth-registration'), data=data)

    def test_registration_process(self):
        # test registration
        data = {
            'first_name': 'Test',
            'phone_number': "+998878493985",
            'password': 'anypassword'
        }

        response = self.client.post(reverse('api:auth-registration'), data=data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Temp.objects.get(phone_number=data['phone_number']).first_name, data.get('first_name'))

        # test activation
        data = {
            "phone_number": '+998878493985',
            'code': '99999'
        }
        response = self.client.post(reverse('api:auth-register-activation'), data=json.dumps(data),
                                    content_type='application/json')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(User.objects.count(), 1)
        self.assertNotEquals(User.objects.get(phone_number=data['phone_number']).password, data.get('password'))
        self.assertIn('pbkdf2_sha', User.objects.get(phone_number=data['phone_number']).password)
        self.assertIn('access_token', response.json())

        # test sign-in
        data = {
            'username': "+998878493985",
            'password': 'anypassword',
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = self.client.post(reverse('api:auth-login'), data=data)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "access_token")
        self.assertContains(response, "refresh_token")

    # def test_registration_inputs(self):
    #     data = {
    #         'first_name': 'Test',
    #         'phone_number': "+9988784939",
    #         'password': '33'
    #     }
    #
    #     response = self.client.post(reverse('api:auth-registration'), data=data)
    #     self.assertEquals(response.json()['phone_number'][-1], 'Ensure this field has at least 12 characters.')
    #
    #     data = {
    #         'first_name': 'Test',
    #         'phone_number': "+998878493339",
    #         'password': '33323333'
    #     }
    #
    #     response = self.client.post(reverse('api:auth-registration'), data=data)
    #     self.assertEquals(response.json()['non_field_errors'][-1], 'This password is entirely numeric.')
    #
    #     data = {
    #         'first_name': 'Test',
    #         'phone_number': "+998878493339",
    #         'password': '33e4g'
    #     }
    #
    #     response = self.client.post(reverse('api:auth-registration'), data=data)
    #     self.assertEquals(response.json()['non_field_errors'][-1],
    #                       'This password is too short. It must contain at least 8 characters.')
    #
    #     data = {
    #         'first_name': 'Test',
    #         'phone_number': "+998878493339",
    #         'password': 'computer'
    #     }
    #
    #     response = self.client.post(reverse('api:auth-registration'), data=data)
    #     self.assertEquals(response.json()['non_field_errors'][-1],
    #                       'This password is too common.')

    def test_incorrect_activation(self, ):
        data = {
            'phone_number': '+998900000000',
            'code': '999990'
        }
        response = self.client.post(reverse('api:auth-register-activation'), data=data)
        self.assertEquals(response.status_code, 400)

    def test_activation_inputs(self, ):
        data = {
            'phone_number': '+998900000000',
            'code': '99f9990'
        }
        response = self.client.post(reverse('api:auth-register-activation'), data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.json()['code'][-1], "A valid integer is required.")


class UserForgetPasswordTestCase(APITestCase):

    def setUp(self):
        self.application = Application.objects.create(authorization_grant_type='password', client_type='confidential')
        self.client_id = self.application.client_id
        self.client_secret = self.application.client_secret
        self.phone_number = "+998900000000"
        data_register = {
            'first_name': 'Test',
            'phone_number': self.phone_number,
            'password': 'anypassword'
        }
        self.client.post(reverse('api:auth-registration'), data=data_register)

        data_activation = {
            'code': '99999',
            'phone_number': self.phone_number
        }
        self.client.post(reverse('api:auth-register-activation'), data=data_activation)
        data = {
            'username': self.phone_number,
            'password': 'anypassword',
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        self.client.post(reverse('api:auth-login'), data=data)

    def test_forget_password_inputs(self):
        # checking less than 12 chars for phone number not allowed
        data = {
            "phone_number": "+8878998887"
        }
        response = self.client.post(reverse('api:forget-pass'), data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.json().get('phone_number')[-1], 'Ensure this field has at least 12 characters.')
        # checking more than 13 chars for phone number not allowed
        data = {
            "phone_number": "+1789980909887"
        }
        response = self.client.post(reverse('api:forget-pass'), data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.json().get('phone_number')[-1], 'Ensure this field has no more than 13 characters.')
        # checking invalid phone number(either a char in phone number or just not valid phone number)
        data = {
            "phone_number": "+9899890909887"
        }
        response = self.client.post(reverse('api:forget-pass'), data=data)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.json().get('phone_number')[0], 'invalid phone number')

    def test_forget_password(self):
        # test forget-pass route after that a code should be sent
        data = {
            "phone_number": self.phone_number
        }
        response = self.client.post(reverse('api:forget-pass'), data=data)
        self.assertEquals(response.status_code, 200)
        self.code = response.json().get('code')

        # test confirm-phone that user inputs the code from sms for confirmation
        data = {
            'code': self.code,
            'phone_number': self.phone_number
        }
        response = self.client.post(reverse('api:confirm-phone'), data=data)
        self.assertContains(response, 'access_token')
        self.access_token = response.json().get('access_token')

        # test password reset with new password and password_confirm
        data = {
            'password': 'newanypassword',
            'password_confirm': 'newanypassword'
        }
        headers = {
            'Authorization': f"Bearer {self.access_token}"
        }
        response = self.client.post(reverse('api:reset-pass'), data=data, headers=headers)
        self.assertEquals(response.status_code, 200)

        # test for password validation auth required
        response = self.client.post(reverse('api:reset-pass'), data=data, )
        self.assertEquals(response.json().get('detail'), 'Authentication credentials were not provided.')
        self.assertEquals(response.status_code, 401)

        # test for password validation(different inputs)
        data = {
            'password': 'new',
            'password_confirm': 'any'
        }
        response = self.client.post(reverse('api:reset-pass'), data=data, headers=headers)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.json().get('password')[-1], 'Passwords not match!')

        # test for password validation(less than 8 chars and too common)
        data = {
            'password': 'new',
            'password_confirm': 'new'
        }
        response = self.client.post(reverse('api:reset-pass'), data=data, headers=headers)
        self.assertEquals(response.status_code, 400)

        # test for password validation(entirely numeric pass not allowed.)
        data = {
            'password': '989898900',
            'password_confirm': '989898900'
        }
        response = self.client.post(reverse('api:reset-pass'), data=data, headers=headers)
        self.assertEquals(response.status_code, 400)
