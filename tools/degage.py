import requests
import re
from icalendar import Calendar

from .utils import str_to_gtime, str_to_degage

MAGIC_STRING = "###autosynced_by_pidgey---dont_remove###"

class Dégage:
    def __init__(self, config):
        self.session = requests.session()
        login_url = "https://degapp.be/login"
        
        self.car = config["car_id"]

        payload = {
            "email": config['degage_email'],
            "password": config['degage_password']
            }
        result = self.session.post(
            login_url, 
            data = payload, 
            headers = dict(referer=login_url))

        if result.status_code != 200:
            raise Exception(f"Wrong credentials for Dégage! Please check config.json")

    def get_events(self):
        out = []
        # Get all ACCEPTED events
        result = self.session.get(
            f"https://degapp.be/trips/page?page=1&pageSize=50&asc=1&orderBy=from&filter=status%3DACCEPTED"
        )
        out += self.parse_events(result)

        # Get all PENDING car requests
        result = self.session.get(
            f"https://degapp.be/trips/page?page=1&pageSize=50&asc=1&orderBy=from&filter=status%3DREQUEST"
        )
        out += self.parse_events(result, prefix="[REQ] ")

        print(f"{len(out)} fetched from Dégage.")
        return out

    def parse_events(self, result, prefix=''):
        """ Parses HTML page and gets trip details """
        out = []
        if result.status_code == 200:
            trips = re.findall(r'(?<=trip\?id=)[0-9]*(?=">Details)', result.text)
            for trip_id in trips:
                result = self.session.get(
                f"https://degapp.be/calendarevents/reservation?id={trip_id}&separator=%0D%0A")
                if result.status_code == 200:
                    out += self.parse_ical_events(result, prefix=prefix)
        else:
            print(f"Something went wrong while getting pending trip requests... {result.text}")

        return out

    def parse_ical_events(self, result, prefix):
        events = Calendar.from_ical(result.text)
        out = []
        for e in events.walk():
            if e.name == "VEVENT":
                start = str_to_gtime(
                    e.get('dtstart').to_ical().decode("utf-8"))
                stop = str_to_gtime(
                    e.get('dtend').to_ical().decode("utf-8"))
                description = e.get('description').to_ical().decode("utf-8")
                _, id = description.rsplit('?id=', 1)
                summary = f"{prefix}{e.get('summary').to_ical().decode('utf-8')}"

                # Determine origin of event
                result = self.session.get(f"https://degapp.be/trip?id={id}")
                origin = 'google' if MAGIC_STRING in result.text else 'degage'
                out.append({
                    'summary': summary,
                    'start': start,
                    'end': stop,
                    'description': description,
                    'id': id,
                    'origin': origin
                })
        return out
    
    def create_event(self, summary, description, start, end, **kwargs):
        data = {
            'name': summary,
            'from': str_to_degage(start), 
            'until': str_to_degage(end),
            'message': MAGIC_STRING,
            'submit': 'default'}
        url = f"https://degapp.be/reservation/create?carId={self.car}"
        result = self.session.post(url, data=data, headers = dict(referer=url))
        if result.status_code == 200:
            print(f"Successfully created reservation in degage from {start} to {end}, {str_to_degage(start)}")
        else:
            print(f"Creating reservation in degage failed: {result.text}")
    
    def delete_event(self, id):
        result = self.session.get(f"https://degapp.be/reservation/cancel?id={id}")
        if result.status_code == 200:
            print(f"Succesfully deleted {id} from degage")
        else:
            print(f"[ERROR] Couldn't delete {id} from degage")


