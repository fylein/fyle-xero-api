from typing import Dict

from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from .helpers import get_fyle_admin
from .models import AuthToken
from .utils import AuthUtils

User = get_user_model()
auth = AuthUtils()


class FyleJWTAuthentication(BaseAuthentication):
    """
    Fyle Authentication class
    """
    def authenticate(self, request):
        """
        Authentication function
        """
        access_token_string = self.get_header(request)

        user = self.validate_token(
            access_token_string=access_token_string,
            origin_address=auth.get_origin_address(request)
        )

        try:
            user = User.objects.get(email=user['email'], user_id=user['user_id'])
            AuthToken.objects.get(user=user)
        except User.DoesNotExist:
            raise ValidationError('User not found for this token')
        except AuthToken.DoesNotExist:
            raise ValidationError('Login details not found for the user')

        return user, None

    @staticmethod
    def get_header(request) -> str:
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get('HTTP_AUTHORIZATION')

        return header

    @staticmethod
    def validate_token(access_token_string: str, origin_address: str) -> Dict:
        """
        Validate the access token
        :param origin_address:
        :param access_token_string:
        :return:
        """
        if not access_token_string:
            raise ValidationError('Access token missing')

        access_token_tokenizer = access_token_string.split(' ')
        if not access_token_tokenizer or len(access_token_tokenizer) != 2 or access_token_tokenizer[0] != 'Bearer':
            raise ValidationError('Invalid access token structure')

        unique_key_generator = access_token_tokenizer[1].split('.')
        email_unique_key = 'email_{0}'.format(unique_key_generator[2])
        user_unique_key = 'user_{0}'.format(unique_key_generator[2])

        email = cache.get(email_unique_key)
        user = cache.get(user_unique_key)

        if not (email and user):
            cache.delete_many([email_unique_key, user_unique_key])

            try:
                employee_info = get_fyle_admin(access_token_string.split(' ')[1], origin_address)
            except Exception:
                raise AuthenticationFailed('Invalid access token')

            cache.set(email_unique_key, employee_info['data']['user']['email'])
            cache.set(user_unique_key, employee_info['data']['user']['id'])

            return {
                'email': employee_info['data']['user']['email'],
                'user_id': employee_info['data']['user']['id']
            }

        elif email and user:
            return {
                'email': email,
                'user_id': user
            }

        raise AuthenticationFailed('Invalid access token')
