# gsheet API
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

# wsgi as gsheet auth handler
import wsgiref.simple_server
import wsgiref.util

# telegram bot
from telegram import Update

import logging
import os

from telegram import Credentials

_LOGGER = logging.getLogger(__name__)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]


def auth(update: Update):
    '''
    Perform authentication for Google Sheet API.
    '''
    creds = None
    
    # try to check the user's existing credential
    if os.path.exists('credentials/credential.json'):
        try:
            creds = Credentials.from_authorized_user_file('credential.json')
        except:
            creds = None

    # if there are no or valid credentials available, then login to auth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            
            host = 'localhost'
            port = '8080'
            wsgi_app = _WSGIApp(success_message='Authentication Success.')

            wsgiref.simple_server.WSGIServer.allow_reuse_address = False
            local_server = wsgiref.simple_server.make_server(
                host, port, wsgi_app, handler_class=_WSGIRequestHandler
            )

            uri = f'http://{host}:{local_server.server_port}/'
            flow = Flow.from_client_secrets_file('secrets.json', SCOPES, redirect_uri=uri)

            # generate authorization url
            auth_url, _ = flow.authorization_url()

            update.message.reply_text(
                f'Please visit this link\n{auth_url}'
            )


class _WSGIApp(object):
    '''
    WSGI app to handle Google Sheet authorization redirect.
    
    Followed official python Google OAuth Lib core functions.
    '''

    def __init__(self, success_message):
        '''
        Args:
            success_message(str): Message to display in the web browser
                the authorization flow is complete
        '''
        self.last_request_uri = None
        self._success_message = success_message

    def __call__(self, environ, start_response):
        '''WSGI Callable.
        
        Args:
            environ (Mapping[str, Any]): The WSGI environment.
            start_response (Callable[str, list]): The WSGI start_response callable.

        Returns:
            Iterable[bytes]: The response body.
        '''

        start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
        self.last_request_uri = wsgiref.util.request_uri(environ)
        return [self._success_message.encode('utf-8')]


class _WSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    '''Custom WSGIRequestHandler.'''

    def log_message(self, format, *args):
        _LOGGER.info(format, *args)