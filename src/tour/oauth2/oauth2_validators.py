from __future__ import unicode_literals

import base64
import binascii
import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import make_aware
from oauthlib.oauth2 import RequestValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .compat import unquote_plus
from .exceptions import FatalClientError
from .models import (
    AccessToken,
    Application,
    Grant,
    RefreshToken,
)
from ..user.models import User
from .scopes import get_scopes_backend

log = logging.getLogger("oauth2_provider")

GRANT_TYPE_MAPPING = {
    "authorization_code": (Application.GRANT_AUTHORIZATION_CODE,),
    "password": (Application.GRANT_PASSWORD,),
    "client_credentials": (Application.GRANT_CLIENT_CREDENTIALS,),
    "refresh_token": (
        Application.GRANT_AUTHORIZATION_CODE,
        Application.GRANT_PASSWORD,
        Application.GRANT_CLIENT_CREDENTIALS,
    )
}

UserModel = get_user_model()


class OAuth2Validator(RequestValidator):

    def __init__(self, client_request=None, access_token=None):
        self.client_request = client_request
        self.access_token = access_token

    def _extract_basic_auth(self, request):
        """
        Return authentication string if request contains basic auth credentials,
        otherwise return None
        """
        auth = request.headers.get("HTTP_AUTHORIZATION", None)
        if not auth:
            return None

        splitted = auth.split(" ", 1)
        if len(splitted) != 2:
            return None
        auth_type, auth_string = splitted

        if auth_type != "Basic":
            return None

        return auth_string

    def _authenticate_basic_auth(self, request):
        """
        Authenticates with HTTP Basic Auth.

        Note: as stated in rfc:`2.3.1`, client_id and client_secret must be encoded with
        "application/x-www-form-urlencoded" encoding algorithm.
        """
        auth_string = self._extract_basic_auth(request)
        if not auth_string:
            return False

        try:
            encoding = request.encoding or settings.DEFAULT_CHARSET or "utf-8"
        except AttributeError:
            encoding = "utf-8"

        try:
            b64_decoded = base64.b64decode(auth_string)
        except (TypeError, binascii.Error):
            log.debug("Failed basic auth: %r can't be decoded as base64", auth_string)
            return False

        try:
            auth_string_decoded = b64_decoded.decode(encoding)
        except UnicodeDecodeError:
            log.debug(
                "Failed basic auth: %r can't be decoded as unicode by %r",
                auth_string, encoding
            )
            return False

        client_id, client_secret = map(unquote_plus, auth_string_decoded.split(":", 1))

        if self._load_application(client_id, request) is None:
            log.debug("Failed basic auth: Application %s does not exist" % client_id)
            return False
        elif request.client.client_id != client_id:
            log.debug("Failed basic auth: wrong client id %s" % client_id)
            return False
        elif request.client.client_secret != client_secret:
            log.debug("Failed basic auth: wrong client secret %s" % client_secret)
            return False
        else:
            return True

    def _authenticate_request_body(self, request):
        """
        Try to authenticate the client using client_id and client_secret
        parameters included in body.

        Remember that this method is NOT RECOMMENDED and SHOULD be limited to
        clients unable to directly utilize the HTTP Basic authentication scheme.
        See rfc:`2.3.1` for more details.
        """
        # TODO: check if oauthlib has already unquoted client_id and client_secret
        try:
            client_id = request.client_id
            client_secret = request.client_secret
        except AttributeError:
            return False

        if self._load_application(client_id, request) is None:
            log.debug("Failed body auth: Application %s does not exists" % client_id)
            return False
        elif request.client.client_secret != client_secret:
            log.debug("Failed body auth: wrong client secret %s" % client_secret)
            return False
        else:
            return True

    def _load_application(self, client_id, request):
        """
        If request.client was not set, load application instance for given
        client_id and store it in request.client
        """

        # we want to be sure that request has the client attribute!
        assert hasattr(request, "client"), '"request" instance has no "client" attribute'

        try:
            request.client = request.client or Application.objects.get(client_id=client_id)
            # Check that the application can be used (defaults to always True)
            if not request.client.is_usable(request):
                log.debug("Failed body authentication: Application %r is disabled" % (client_id))
                return None
            return request.client
        except Application.DoesNotExist:
            log.debug("Failed body authentication: Application %r does not exist" % (client_id))
            return None

    def client_authentication_required(self, request, *args, **kwargs):
        """
        Determine if the client has to be authenticated

        This method is called only for grant types that supports client authentication:
            * Authorization code grant
            * Resource owner password grant
            * Refresh token grant

        If the request contains authorization headers, always authenticate the client
        no matter the grant type.

        If the request does not contain authorization headers, proceed with authentication
        only if the client is of type `Confidential`.

        If something goes wrong, call oauthlib implementation of the method.
        """
        if self._extract_basic_auth(request):
            return True

        try:
            if request.client_id and request.client_secret:
                return True
        except AttributeError:
            log.debug("Client ID or client secret not provided...")
            pass

        self._load_application(request.client_id, request)

        if request.client:
            return request.client.client_type == Application.CLIENT_CONFIDENTIAL

        return super(OAuth2Validator, self).client_authentication_required(request,
                                                                           *args, **kwargs)

    def authenticate_client(self, request, *args, **kwargs):
        """
        Check if client exists and is authenticating itself as in rfc:`3.2.1`

        First we try to authenticate with HTTP Basic Auth, and that is the PREFERRED
        authentication method.
        Whether this fails we support including the client credentials in the request-body,
        but this method is NOT RECOMMENDED and SHOULD be limited to clients unable to
        directly utilize the HTTP Basic authentication scheme.
        See rfc:`2.3.1` for more details
        """
        authenticated = self._authenticate_basic_auth(request)

        if not authenticated:
            authenticated = self._authenticate_request_body(request)

        return authenticated

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        """
        If we are here, the client did not authenticate itself as in rfc:`3.2.1` and we can
        proceed only if the client exists and is not of type "Confidential".
        """
        if self._load_application(client_id, request) is not None:
            log.debug("Application %r has type %r" % (client_id, request.client.client_type))
            return request.client.client_type != Application.CLIENT_CONFIDENTIAL
        return False

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, *args, **kwargs):
        """
        Ensure the redirect_uri is listed in the Application instance redirect_uris field
        """
        grant = Grant.objects.get(code=code, application=client)
        return grant.redirect_uri_allowed(redirect_uri)

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        """
        Remove the temporary grant used to swap the authorization token
        """
        grant = Grant.objects.get(code=code, application=request.client)
        grant.delete()

    def validate_client_id(self, client_id, request, *args, **kwargs):
        """
        Ensure an Application exists with given client_id.
        If it exists, it's assigned to request.client.
        """
        return self._load_application(client_id, request) is not None

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        return request.client.default_redirect_uri

    def _get_token_from_authentication_server(self, token, introspection_url, introspection_token):
        bearer = "Bearer {}".format(introspection_token)

        try:
            response = requests.post(
                introspection_url,
                data={"token": token}, headers={"Authorization": bearer}
            )
        except requests.exceptions.RequestException:
            log.exception("Introspection: Failed POST to %r in token lookup", introspection_url)
            return None

        try:
            content = response.json()
        except ValueError:
            log.exception("Introspection: Failed to parse response as json")
            return None

        if "active" in content and content["active"] is True:
            if "username" in content:
                user, _created = UserModel.objects.get_or_create(
                    **{UserModel.USERNAME_FIELD: content["username"]}
                )
            else:
                user = None

            max_caching_time = datetime.now() + timedelta(
                days=30
            )

            if "exp" in content:
                expires = datetime.utcfromtimestamp(content["exp"])
                if expires > max_caching_time:
                    expires = max_caching_time
            else:
                expires = max_caching_time

            scope = content.get("scope", "")
            expires = make_aware(expires)

            try:
                access_token = AccessToken.objects.select_related("application", "user").get(token=token)
            except AccessToken.DoesNotExist:
                access_token = AccessToken.objects.create(
                    token=token,
                    user=user,
                    application=None,
                    scope=scope,
                    expires=expires
                )
            else:
                access_token.expires = expires
                access_token.scope = scope
                access_token.save()

            return access_token

    def validate_bearer_token(self, token, scopes, request):
        """
        When users try to access resources, check that provided token is valid
        """
        if not token:
            return False

        introspection_url = None
        introspection_token = None

        try:
            access_token = AccessToken.objects.select_related("application", "user").get(token=token)
            # if there is a token but invalid then look up the token
            if introspection_url and introspection_token:
                if not access_token.is_valid(scopes):
                    access_token = self._get_token_from_authentication_server(
                        token,
                        introspection_url,
                        introspection_token
                    )

            if access_token and access_token.is_valid(scopes):
                request.client = access_token.application
                request.user = access_token.user
                request.scopes = scopes

                # this is needed by django rest framework
                request.access_token = access_token
                return True
            return False
        except AccessToken.DoesNotExist:
            # there is no initial token, look up the token
            if introspection_url and introspection_token:
                access_token = self._get_token_from_authentication_server(
                    token,
                    introspection_url,
                    introspection_token
                )
                if access_token and access_token.is_valid(scopes):
                    request.client = access_token.application
                    request.user = access_token.user
                    request.scopes = scopes

                    # this is needed by django rest framework
                    request.access_token = access_token
                    return True
            return False

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        try:
            grant = Grant.objects.get(code=code, application=client)
            if not grant.is_expired():
                request.scopes = grant.scope.split(" ")
                request.user = grant.user
                return True
            return False

        except Grant.DoesNotExist:
            return False

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """
        Validate both grant_type is a valid string and grant_type is allowed for current workflow
        """
        assert (grant_type in GRANT_TYPE_MAPPING)  # mapping misconfiguration
        return request.client.allows_grant_type(*GRANT_TYPE_MAPPING[grant_type])

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        """
        We currently do not support the Authorization Endpoint Response Types registry as in
        rfc:`8.4`, so validate the response_type only if it matches "code" or "token"
        """
        if response_type == "code":
            return client.allows_grant_type(Application.GRANT_AUTHORIZATION_CODE)
        elif response_type == "token":
            return client.allows_grant_type(Application.GRANT_IMPLICIT)
        else:
            return False

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        Ensure required scopes are permitted (as specified in the settings file)
        """
        available_scopes = get_scopes_backend().get_available_scopes(application=client, request=request)
        return set(scopes).issubset(set(available_scopes))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        default_scopes = get_scopes_backend().get_default_scopes(application=request.client, request=request)
        return default_scopes

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return request.client.redirect_uri_allowed(redirect_uri)

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        expires = timezone.now() + timedelta(
            seconds=60)
        g = Grant(application=request.client, user=request.user, code=code["code"],
                  expires=expires, redirect_uri=request.redirect_uri,
                  scope=" ".join(request.scopes))
        g.save()

    def rotate_refresh_token(self, request):
        """
        Checks if rotate refresh token is enabled
        """
        return True

    @transaction.atomic
    def save_bearer_token(self, token, request, *args, **kwargs):
        """
        Save access and refresh token, If refresh token is issued, remove or
        reuse old refresh token as in rfc:`6`

        @see: https://tools.ietf.org/html/draft-ietf-oauth-v2-31#page-43
        """

        if "scope" not in token:
            raise FatalClientError("Failed to renew access token: missing scope")

        expires = timezone.now() + timedelta(days=30)

        if request.grant_type == "client_credentials":
            request.user = None

        # This comes from OAuthLib:
        # https://github.com/idan/oauthlib/blob/1.0.3/oauthlib/oauth2/rfc6749/tokens.py#L267
        # Its value is either a new random code; or if we are reusing
        # refresh tokens, then it is the same value that the request passed in
        # (stored in `request.refresh_token`)
        refresh_token_code = token.get("refresh_token", None)

        if refresh_token_code:

            # an instance of `RefreshToken` that matches the old refresh code.
            # Set on the request in `validate_refresh_token`
            refresh_token_instance = getattr(request, "refresh_token_instance", None)

            # If we are to reuse tokens, and we can: do so
            if not self.rotate_refresh_token(request) and \
                    isinstance(refresh_token_instance, RefreshToken) and \
                    refresh_token_instance.access_token:
                access_token = AccessToken.objects.select_for_update().get(
                    pk=refresh_token_instance.access_token.pk
                )
                access_token.user = request.user
                access_token.scope = token["scope"]
                access_token.expires = expires
                access_token.token = token["access_token"]
                access_token.application = request.client
                access_token.save()

            # else create fresh with access & refresh tokens
            else:
                # revoke existing tokens if possible
                if isinstance(refresh_token_instance, RefreshToken):
                    try:
                        access_token = refresh_token_instance.access_token
                        access_token.token = token["access_token"]
                        access_token.expires = expires
                        access_token.save()

                        refresh_token_instance.revoke()


                    except (AccessToken.DoesNotExist, RefreshToken.DoesNotExist):
                        pass
                        # raise serializers.ValidationError({[_('not found AccessToken ')]})
                    else:
                        setattr(request, "refresh_token_instance", None)
                else:
                    access_token = self._create_access_token(expires, request, token)

                # access_token = self._create_access_token(expires, request, token)

                refresh_token = RefreshToken(
                    user=request.user,
                    token=refresh_token_code,
                    application=request.client,
                    access_token=access_token,
                    expires=timezone.now() + timedelta(days=365)
                )
                refresh_token.save()

        # No refresh token should be created, just access token
        else:
            self._create_access_token(expires, request, token)

        # TODO: check out a more reliable way to communicate expire time to oauthlib
        token["expires_in"] = str(timezone.now() + timedelta(days=30))

    def _create_access_token(self, expires, request, token):
        access_token = AccessToken(
            user=request.user,
            scope=token["scope"],
            expires=expires,
            token=token["access_token"],
            application=request.client
        )
        access_token.save()
        return access_token

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        """
        Revoke an access or refresh token.

        :param token: The token string.
        :param token_type_hint: access_token or refresh_token.
        :param request: The HTTP Request (oauthlib.common.Request)
        """
        if token_type_hint not in ["access_token", "refresh_token"]:
            token_type_hint = None

        token_types = {
            "access_token": AccessToken,
            "refresh_token": RefreshToken,
        }

        token_type = token_types.get(token_type_hint, AccessToken)
        try:
            token_type.objects.get(token=token).revoke()
        except ObjectDoesNotExist:
            for other_type in [_t for _t in token_types.values() if _t != token_type]:
                # slightly inefficient on Python2, but the queryset contains only one instance
                list(map(lambda t: t.revoke(), other_type.objects.filter(token=token)))

    def validate_user(self, username, password, client, request, *args, **kwargs):
        """
        Check username and password correspond to a valid and active User
        """
        u = authenticate(username=username, password=password)
        if u is not None and u.is_active:
            request.user = u
            return True
        return False

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Avoid second query for RefreshToken since this method is invoked *after*
        # validate_refresh_token.
        rt = request.refresh_token_instance
        return rt.access_token.scope

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        """
        Check refresh_token exists and refers to the right client.
        Also attach User instance to the request object
        """
        try:
            rt = RefreshToken.objects.get(token=refresh_token)
            request.user = rt.user
            request.refresh_token = rt.token
            # Temporary store RefreshToken instance to be reused by get_original_scopes.
            request.refresh_token_instance = rt
            return rt.application == client
            # if rt.is_valid():
            # else:
            #     raise ValidationError(
            #         {'message': 'Refresh Token expired. You should confirm your phone number and get new one!'})

        except RefreshToken.DoesNotExist:
            return False


class OAuth2V1Validator(OAuth2Validator):

    def validate_user(self, username, password, client, request, *args, **kwargs):
        u = self.get_user(username, password)

        if u is not None and u.is_active:
            request.user = u
            return True
        return False

    def get_user(self, username, password):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'username': ['invalid email or password']})

        if check_password(password, user.password):
            return user


class OAuth2FrontValidator(OAuth2Validator):

    def validate_user(self, username, password, client, request, *args, **kwargs):
        u = self.get_user(username, password)

        if u is not None and u.is_active:
            request.user = u
            return True
        return False

    def get_user(self, username, password):
        try:
            user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone_number': ['invalid username or password']})

        if check_password(password, user.password):
            return user
