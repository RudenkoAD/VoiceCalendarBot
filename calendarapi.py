from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SET_TIMEZONE = "Europe/Moscow"
GET_TIMEZONE = "+03:00"
class CalendarAPI:
  SCOPES = ["https://www.googleapis.com/auth/calendar"]
  def __init__(self, user_id, set_time_zone=SET_TIMEZONE, get_time_zone=GET_TIMEZONE):
    # Load the credentials from the service account key file
    credentials = self.create_credentials(user_id)
    self.set_time_zone = set_time_zone
    self.get_time_zone = get_time_zone
    # Build the Google Calendar API service
    self.service = build('calendar', 'v3', credentials=credentials)

  
  def create_credentials(self, user_id):
    creds = None
    path = os.path.join("data", "user_creds", f"{user_id}.json")
    if os.path.exists(path):
      creds = Credentials.from_authorized_user_file(path, self.SCOPES)
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
      with open(path, "w") as token:
        token.write(creds.to_json())
    return creds

  def add_event_to_calendar(self, name, start_time, end_time):
    # Create the event body
    event = {
      'summary': name,
      'start': {
        'dateTime': start_time,
        'timeZone': self.set_time_zone,
      },
      'end': {
        'dateTime': end_time,
        'timeZone': self.set_time_zone,
      },
    }

    # Call the API to insert the event
    event = self.service.events().insert(calendarId='primary', body=event).execute()

    print(f'Event "{event["summary"]}" added to Google Calendar.')
    return event["id"]
    #return f"Event added with ID = {event['id']}"

  def remove_event_from_calendar(self, id):
    # Call the API to delete the event
    self.service.events().delete(calendarId='primary', eventId=id).execute()

    return('Event removed from Google Calendar.')


  def get_event_by_id(self, event_id):
    # Call the API to get the event
    event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

    return event

  def get_events_at_time(self, start_time, end_time):
    # Call the API to list events
    start_time+=self.get_time_zone
    end_time+=self.get_time_zone
    response = self.service.events().list(calendarId='primary', timeMin=start_time, timeMax=end_time).execute()
    
    if 'items' in response and len(response['items']) > 0:
      return "Events found: " + str([item for item in response['items']])
    else:
      return "No events found"

  def get_events_by_name(self, name):
    #name may not be 100% accurate
    
    # Call the API to list events
    response = self.service.events().list(calendarId='primary', q=name).execute()
    
    if 'items' in response and len(response['items']) > 0:
      return "Events found: " + str([item for item in response['items']])
    else:
      return "No events found"

def main():
  calendar = CalendarAPI(user_id=1)
  id = calendar.add_event_to_calendar("Test event", "2023-12-18T12:00:00z", "2023-12-18T13:00:00z")
  calendar.get_events_at_time("2023-12-18T00:00:00", "2023-12-19T00:00:00")
  calendar.get_events_by_name("Test event")
  calendar.remove_event_from_calendar(id)
  
if __name__ == '__main__':
    main()