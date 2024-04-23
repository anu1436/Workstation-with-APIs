from flask import Flask, render_template
import requests
import os.path
from datetime import datetime  # Import just the datetime class
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

# You can use scopes based on your requirements
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_events():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(calendarId="primary", timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy="startTime").execute()
    events = events_result.get("items", [])
    if not events:
        print("No upcoming events found.")
        return []
    
    formatted_events = []
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        event_str = f"{event['summary']} at {start_time}"
        formatted_events.append(event_str)
    
    return formatted_events


def get_current_time(timezone='Etc/UTC'):
    response = requests.get(f'http://worldtimeapi.org/api/timezone/{timezone}')
    time_data = response.json()
    
    current_datetime = time_data['datetime'] 
    utc_offset = time_data['utc_offset']
    timezone_name = time_data['timezone']
    
    time_formatted = f"{current_datetime} (UTC Offset: {utc_offset}, Timezone: {timezone_name})"
    
    return time_formatted

def get_youtube_embed_url(video_url):
    video_id = video_url.split('=')[-1]
    youtube_embed_url = f"https://www.youtube.com/embed/{video_id}"
    return youtube_embed_url

@app.route('/')
def index():
    tasks = get_calendar_events() 
    time = get_current_time('Asia/Kolkata')
    youtube_player = get_youtube_embed_url('https://www.youtube.com/watch?v=5qap5aO4i9A')
    return render_template('index.html', tasks=tasks, time=time, youtube_player=youtube_player)

if __name__ == '__main__':
    app.run(debug=True)
