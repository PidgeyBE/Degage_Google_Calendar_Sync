from __future__ import print_function
import os
import datetime
import time
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

from .utils import str_to_gtime, TIMEZONE_STR, str_to_rfc3339

def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service


class GCalendar:
    def __init__(self, config):
        # Set up connection to Google Cloud
        self.calendar_id = config['calendar_id']
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        key_file_location = os.path.join(os.path.dirname(__file__), os.pardir, 'service_account.json')

        self.service = get_service(
            api_name='calendar',
            api_version='v3',
            scopes=SCOPES,
            key_file_location=key_file_location)
    
    def get_events(self):
        page_token = None
        events=[]
        d = datetime.datetime.utcnow()
        time_min = d.isoformat("T") + "Z"
        while True:
            g_events = self.service.events().list(
                calendarId=self.calendar_id, pageToken=page_token, timeMin=time_min).execute()
            if g_events['items']:
                events += g_events['items']
            page_token = g_events.get('nextPageToken')
            if not page_token:
                break
        print(f"{len(events)} fetched from Google.")

        out = []
        for event in events:
            if 'date' in event['start']:
                start = str_to_gtime(event['start']['date'])
                stop = str_to_gtime(event['end']['date'])
            else:
                # strip timezone
                start = event['start']['dateTime']
                stop = event['end']['dateTime']

                start = str_to_gtime(start)
                stop = str_to_gtime(stop)

            description = event.get('description', '')
            out.append({
                'summary': event.get('summary', ''),
                'start': start,
                'end': stop,
                'description': description,
                'id': event['id'],
                'origin': 'degage' if "https://degapp.be/trip?id=" in description else "google"
            })

        return out
    
    def get_calendars(self):
        calendar_list = self.service.calendarList().list(pageToken=None).execute()
        print(calendar_list)


    def create_event(self, summary, description, start, end, **kwargs):
        event = {
            'summary': summary,
            'location': '',
            'description': description,
            'start': {
                'dateTime': f'{str_to_rfc3339(start)}',  # timezone via timezone attribute
                'timeZone': TIMEZONE_STR,
            },
            'end': {
                'dateTime': f'{str_to_rfc3339(end)}',
                'timeZone': TIMEZONE_STR,
            }
            }
     
        event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        # google api has a rate limit...
        time.sleep(1)
        print(f"Successfully created Google event at {start}-{end}: {event.get('htmlLink')}")

    def delete_event(self, event_id):
        self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
        print(f"Deleted {event_id} on GCalendar")
        time.sleep(1)