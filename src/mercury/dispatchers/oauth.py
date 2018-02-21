# -*- coding: utf-8 -*-
import abc
import datetime
import urllib
from urllib.parse import parse_qs

from constance import config
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from oauth2client.client import EXPIRY_FORMAT, OAuth2Credentials
from requests_oauthlib import OAuth2Session
from strategy_field.utils import fqn


def credentials_from_dict(client_id, in_data):
    data = dict(in_data)
    if (data.get('token_expiry') and
            not isinstance(data['token_expiry'], datetime.datetime)):
        try:
            data['token_expiry'] = datetime.datetime.strptime(
                data['token_expiry'], EXPIRY_FORMAT)
        except ValueError:
            data['token_expiry'] = None

    retval = OAuth2Credentials(
        access_token=data['access_token'],
        client_id=client_id,  # data['client_id'],
        client_secret=settings.OAUTH_CLIENT_SECRET,  # data['client_secret'],
        refresh_token=data.get('refresh_token', None),
        token_expiry=data.get('expires_at', None),
        token_uri=data.get('token_uri', 'https://accounts.google.com/o/oauth2/token'),
        user_agent='Mercury',
        revoke_uri=data.get('revoke_uri', None),
        id_token=data.get('id_token', None),
        id_token_jwt=data.get('id_token_jwt', None),
        token_response=data.get('token_response', None),
        scopes=data.get('scopes', None),
        token_info_uri=data.get('token_info_uri', None))
    retval.invalid = data.get('invalid', False)
    return retval


class OAauthHAndlerBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def oauth_success(self, request: WSGIRequest, session: OAuth2Session):
        pass

    @abc.abstractmethod
    def oauth_failure(self, request: WSGIRequest):
        pass

    @abc.abstractmethod
    def oauth_request(self, request: WSGIRequest, redirect_to=None):
        pass

    @abc.abstractmethod
    def oauth_callback(self, request: WSGIRequest):
        pass


class OAauthHAndler(OAauthHAndlerBase):
    authorization_url = ''
    fetch_token_url = ''
    authorization_extra_kwargs = {}
    fetch_token_extra_kwargs = {}
    scopes = []

    client_id = ''
    client_secret = ''

    def _get_state(self, request: WSGIRequest, redirect_to=None):
        if request.GET.get('state', None):
            return request.GET['state']
        else:
            return urllib.parse.urlencode({"channel": self.owner.pk,
                                           "handler": fqn(self),
                                           "redirect_to": redirect_to or "",
                                           })

    def save_credentials(self, c: OAuth2Credentials, commmit=False):
        expires_time = None
        if isinstance(c.token_expiry, datetime.datetime):
            expires_time = c.token_expiry.strftime(EXPIRY_FORMAT)
        elif isinstance(c.token_expiry, (int, float)):
            expires_time = datetime.datetime.fromtimestamp(c.token_expiry).strftime(EXPIRY_FORMAT)
        elif isinstance(c.token_expiry, str):
            try:
                expires_time = datetime.datetime.fromtimestamp(int(c.token_expiry)).strftime(EXPIRY_FORMAT)
            except ValueError:
                expires_time = c.token_expiry

        data = {
            'access_token': c.access_token,
            'expires_time': expires_time,
            # 'token_expiry': c.token_expiry,
            'id_token': c.id_token,
            'token_type': '',
            'refresh_token': c.refresh_token,
        }
        self.owner.config['credentials'] = data
        if commmit:
            self.owner.save()

    def oauth_success(self, request: WSGIRequest, session: OAuth2Session):
        self.owner.config = {'credentials': session.token}
        self.owner.save()

    def oauth_failure(self, request):
        pass

    def get_session(self, request, redirect_to=None):
        redirect_uri = config.OAUTH_CALLBACK
        state = self._get_state(request, redirect_to)
        return OAuth2Session(self.client_id,
                             redirect_uri=redirect_uri,
                             state=state,
                             scope=self.scopes)

    def oauth_request(self, request, redirect_to=None):
        # redirect_uri = config.OAUTH_CALLBACK
        # state = self._get_state(request, redirect_to)
        # session = OAuth2Session(self.client_id,
        #                         redirect_uri=redirect_uri,
        #                         state=state,
        #                         scope=self.scopes)
        session = self.get_session(request, redirect_to)

        authorization_url, state = session.authorization_url(
            self.authorization_url,
            **self.authorization_extra_kwargs)
        return HttpResponseRedirect(authorization_url)

    def oauth_callback(self, request):
        if 'error' in request.GET:
            return self.oauth_failure(request)
        else:
            session = self.get_session(request)
            # state = request.GET['state']
            # args = parse_qs(state)
            # session = OAuth2Session(self.client_id,
            #                         redirect_uri=config.OAUTH_CALLBACK,
            #                         state=state,
            #                         scope=self.scopes)
            session.fetch_token(
                self.fetch_token_url,
                authorization_response=request.get_full_path(),
                **self.fetch_token_extra_kwargs
            )
            self.oauth_success(request, session)

        args = parse_qs(session.state)
        if args['redirect_to']:
            return HttpResponseRedirect(args['redirect_to'][0])

    # def refresh_token(self):
    #     try:
    #         session = self.get_session(None)
    #         session.refresh_token(token_url=self.authorization_url,
    #                               refresh_token=self.config['credentials']['refresh_token'])
    #         # FIXME: remove me (print)
    #         print(111, session.token)
    #         return session.token
    #     except Exception as e:
    #         self.logger.exception(e)
    #         raise
