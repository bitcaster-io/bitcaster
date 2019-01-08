# -*- coding: utf-8 -*-
import base64
import datetime
from email.mime.text import MIMEText

import httplib2
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from googleapiclient.discovery import Resource, build
from oauth2client.client import EXPIRY_FORMAT, HttpAccessTokenRefreshError
from requests_oauthlib import OAuth2Session
from rest_framework import serializers
from strategy_field.utils import fqn

from bitcaster.dispatchers.base import (Dispatcher, DispatcherOptions,
                                        MessageType,)
from bitcaster.dispatchers.oauth import OAauthHAndler, credentials_from_dict
from bitcaster.dispatchers.registry import dispatcher_registry


class EmailMessage(MessageType):
    has_subject = True
    allow_html = True


# https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=<ACCESS_TOKEN>
class GmailOAauthHAndler(OAauthHAndler):
    authorization_url = 'https://accounts.google.com/o/oauth2/auth'
    fetch_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorization_extra_kwargs = {'access_type': 'offline',
                                  'include_granted_scopes': 'true',
                                  'prompt': 'select_account'}
    fetch_token_extra_kwargs = {'client_secret': settings.GOOGLE_APP_SECRET}
    scopes = ['https://www.googleapis.com/auth/gmail.send',
              # 'https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.metadata',
              # 'https://www.googleapis.com/auth/gmail.settings.basic',
              ]

    def oauth_success(self, request: WSGIRequest, session: OAuth2Session):
        expires = int(session.token['expires_at']) + int(session.token['expires_in'])
        exp = datetime.datetime.fromtimestamp(expires).strftime(EXPIRY_FORMAT)
        data = {
            'access_token': session.token['access_token'],
            'token_type': session.token['token_type'],

            # 'expires_in': session.token['expires_in'],
            # 'expires_at': session.token['expires_at'],
            'token_expiry': exp,

            'id_token': session.token.get('id_token'),
            'refresh_token': session.token.get('refresh_token'),
        }
        credentials = credentials_from_dict(data)
        http = credentials.authorize(httplib2.Http())
        service = build('gmail', 'v1', http=http)
        profile = (service.users().getProfile(userId='me')).execute()

        self.owner.config = {'credentials': data,
                             'sender': profile['emailAddress']}
        self.owner.save()


class SubscriptionOptions(serializers.Serializer):
    pass


class GmailOAuthOptions(DispatcherOptions):
    credentials = serializers.JSONField()
    sender = serializers.EmailField(required=True)


@dispatcher_registry.register
class GmailOAuth(Dispatcher, GmailOAauthHAndler):
    options_class = GmailOAuthOptions
    message_class = EmailMessage
    subscription_class = SubscriptionOptions

    def _get_connection(self) -> Resource:
        data = self.config
        credentials = credentials_from_dict(data['credentials'])
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)
        self.save_credentials(credentials, True)
        return build('gmail', 'v1', http=http)

    def emit(self, subscription, subject, message, connection=None, *args, **kwargs):
        recipient = self.get_recipient_address(subscription)
        try:
            service = self._get_connection()
            message = MIMEText(message)
            message['to'] = recipient.email
            message['from'] = self.config['sender']
            message['subject'] = subject
            msg = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            message = (service.users().messages().send(userId='me',
                                                       body=msg)
                       .execute())

            self.logger.debug('{0} email sent to {1.email}'.format(fqn(self), recipient))
            return 1
        except Exception as e:
            self.logger.exception(e)

    def test_connection(self, raise_exception=False):
        try:
            service = self._get_connection()
            profile = (service.users().getProfile(userId='me')).execute()
            return profile
        except HttpAccessTokenRefreshError:
            self.refresh_token()
        except Exception as error:
            self.logger.exception(error)
            raise
