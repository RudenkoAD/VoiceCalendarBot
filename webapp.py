import flask
from io import BytesIO
from flask import request, redirect, session, abort, send_file
from google.oauth2 import id_token
import requests
import os.path
webapp = flask.Flask(__name__)
#set secret key for session
webapp.secret_key = os.environ["WEBAPP_SECRET_KEY"]


from google_auth_oauthlib.flow import Flow
SCOPES = ["https://www.googleapis.com/auth/calendar"]
flow = Flow.from_client_secrets_file("credentials.json", SCOPES, redirect_uri="http://localhost/callback")

@webapp.route("/")
def home():
  return redirect("/login")

@webapp.route("/login")
def login():
  autho_url, state = flow.authorization_url(prompt='consent')
  session["state"] = state
  session["id"] = request.args.get('id', '')
  return redirect(autho_url)

@webapp.route("/callback")
def callback():
  flow.fetch_token(authorization_response=request.url)
  creds = flow.credentials
  if not session["state"] == request.args["state"]:
      abort(500)  # State does not match!
  path = os.path.join("creds", f"{session['id']}.json")
  with open(path, "w") as token:
    token.write(creds.to_json())
  return redirect("/done")

@webapp.route("/done")
def done():
  return "Done! You may return to the telegram bot now."

if __name__ == "__main__":
  context = ('certificate/certificate.crt', 'certificate/private.key')
  webapp.run(host="0.0.0.0", port=80, ssl_context = context)#ssl_context='adhoc'