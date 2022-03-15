import os.path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import wsgiref.simple_server
import wsgiref.util
import logging

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]
_LOGGER = logging.getLogger(__name__)


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



host = 'localhost'
port = 8080
wsgi_app = _WSGIApp(success_message='Authentication Success.')

wsgiref.simple_server.WSGIServer.allow_reuse_address = False
local_server = wsgiref.simple_server.make_server(
    host, port, wsgi_app, handler_class=_WSGIRequestHandler
)

uri = f'http://{host}:{local_server.server_port}/'

flow = Flow.from_client_secrets_file('secrets.json', SCOPES, redirect_uri=uri)

# generate authorization url
auth_url, _ = flow.authorization_url()
print(auth_url)
local_server.handle_request()
# TODO: Create a simple WSGI as redirect URI
print(wsgi_app.last_request_uri)
# token = input('Input token: ')
status = flow.fetch_token(authorization_response=wsgi_app.last_request_uri.replace('http', 'https'))
print('Authorization success.' if status else 'Authorizatoin Failed.')

# try:
#     service = build('sheets', 'v4', credentials=creds)

#     sheet = service.spreadsheets()
#     template = {
#         'properties': {
#             'title': 'Monte Bot Test'
#         }
#     }
#     crsheet = sheet.create(body=template, fields='spreadsheetId').execute()
#     print('Spreadsheet ID: {0}'.format(crsheet.get('spreadsheetId')))


# except HttpError as err:
#     print(err)