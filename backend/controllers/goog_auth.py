import os
import flask
import requests
from flask import Blueprint, request, g
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from environment.config import secret
from serializers.user import UserSchema
from models.user import User
from app import db, ma
import datetime
import json
from serializers.user_populate import UserPopSchema


# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# # Note: A secret key is included in the sample so that it works.
# # If you use this code in your application, replace this with a truly secret
# # key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'random key'


user_schema = UserSchema()
user_pop_schema = UserPopSchema()


router = Blueprint(__name__, 'goog_auth')

@router.route('/goog')
def index():
  return print_index_table()


@router.route('/calendar_actions/<int:id>', methods=['GET','POST'])
def handle_google_calendar(id):
  event_request = request.get_json()
  print("EVENT RESULT HERE:", event_request)

  flask.session['userID'] = id
  result = db.engine.execute(f"""SELECT "google_Auth_Token" FROM users WHERE id = {id};""")
  for i in result:
    print("<----------------------INFO START---------------------->")
    print('A LITTLE TEST:', i[0])
    print("<----------------------INFO END---------------------->")
    if i[0] == 'Unregistered':
      print("IT IS!!")
      # return flask.redirect(f'authorize')
      return flask.redirect('https://project-4-rmbr.herokuapp.com/api/calendar_actions/authorize')


  result = db.engine.execute(f"""SELECT "google_Auth_Token" FROM users WHERE id = {id};""")
  for i in result:
    # print('TEST CREDS:', i[0])
    credentials = google.oauth2.credentials.Credentials(
          **json.loads(i[0]))
  print('CREDENTIALS HERE:', credentials)

  service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
  print('Getting the upcoming 10 events')
  events_result = service.events().list(calendarId='primary', timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()



  # Save credentials back to session in case access token was refreshed.
 
  flask.session['credentials'] = credentials_to_dict(credentials)
  print('_________________________PRINT TEST_____________')
  print('event_request:', event_request)
  print('_________________________PRINT TEST END_____________')
  print("USER TOKEN INFO", db.engine.execute(f"""UPDATE users SET "google_Auth_Token" = '{json.dumps(flask.session['credentials'])}' WHERE id = {id};"""))

  if event_request is not None:
    print('SUBMITTING TO CALENDAR...', event_request)
    event_request = service.events().insert(calendarId='primary', body=event_request).execute()
    
    

    add_event = service.events().insert(calendarId='primary', )


  events = events_result.get('items', [])
  if not events:
        print('No upcoming events found.')
  for event in events:
      start = event['start'].get('dateTime', event['start'].get('date'))
      print(start, event['summary'])

  return 'Successfully connected rmbr to your google calendar! You can close this tab now!', 200


@router.route('/calendar_actions/authorize')
def authorize():
  
  print('start flow')
  id = flask.session['userID']
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  print(f'Current User ID: {id}')


  flow.redirect_uri = flask.url_for(f'controllers.goog_auth.oauth2callback',  _external=True, _scheme='https')
  # print('start flow3')
  print('redirect:', flow.redirect_uri)
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline', include_granted_scopes='false')
  # print('start flow4')
  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state
  
  # print('start flow5')

  print(flask.session)
  print(flask.session['userID'])
  print('_________AUTHORIZATION URL:_________', authorization_url)
  return (authorization_url)
  # return flask.redirect(authorization_url)


@router.route('/oauth2callback')
def oauth2callback():
  id = flask.session['userID']
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  print("<----------------------GOT SENT TO REGISTER PAGE---------------------->")
  # print(user_id)
  state = flask.session['state']

  # print("<----------------------End of STATE---------------------->")
  

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('controllers.goog_auth.oauth2callback', _external=True, _scheme='https')

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url

  authorization_response = authorization_response.replace('http', 'https')
  print("|||||||||||||||||||AUTHORIZATION RESPONSE:|||||||||||||||||||", authorization_response)
  print('|||||||||||||||||||AUTHORIZATION END|||||||||||||||||||')
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials

  
  flask.session['credentials'] = credentials_to_dict(credentials)
  print("USER TOKEN INFO", db.engine.execute(f"""UPDATE users SET "google_Auth_Token" = '{json.dumps(flask.session['credentials'])}' WHERE id = {id};"""))

  return flask.redirect(flask.url_for('controllers.goog_auth.handle_google_calendar', id= flask.session['userID'], _scheme='https',  _external=True))


@router.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@router.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  dicti = {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}
  # print("DICTIONARY TOKENS HERE:", dicti)
  return dicti

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080)