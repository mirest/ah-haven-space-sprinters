import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

from config.settings.default import SECRET_KEY

"""Configure JWT Here"""
class JWTAuthentication(authentication.BaseAuthentication):
	"""docstring for JWTAuthentication"""
	authentication_header_prefix = 'Bearer'

	def authenticate(self, request):
		auth_headers = authentication.get_authorization_header(request).split()

		auth_header_prefix = self.authentication_header_prefix.lower()

		if not auth_headers:
			return None

		if len(auth_headers) == 1 or len(auth_headers) > 2:
			return None

		prefix = auth_headers[0].decode('utf-8')
		token = auth_headers[1].decode('utf-8')

		if prefix.lower() != auth_header_prefix:

			return None

		return self._authenticate_credentials(request, token)

	def _authenticate_credentials(self, request, token):

		try:
			payload = jwt.decode(token, SECRET_KEY)
		except jwt.InvalidTokenError or jwt.DecodeError:
			msg = 'Invalid authentication. Could not decode token.'
			raise exceptions.AuthenticationFailed(msg)

		except jwt.ExpiredSignature:
			msg = 'Token has expired. please login again'
			raise exceptions.AuthenticationFailed(msg)

		try:
			user = User.objects.get(username=payload['username'])
		except User.DoesNotExist:
			msg = 'No user matching this token was found.'
			raise exceptions.AuthenticationFailed(msg)

		if not user.is_active:
			msg = 'This user has been deactivated.'
			raise exceptions.AuthenticationFailed(msg)

		return (user, token)
