import datetime
import time
import os
import json
import datetime

from tools.gcloud import GCalendar
from tools.degage import Dégage
from tools.events import EventRegistry
from tools.utils import is_started, now_str

# read configs
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    configs = json.loads(f.read())

# For each config (=degage account + gcalendar), do the syncing
for config in configs:
    print(f"{now_str()}: Starting sync for {config['degage_email']}")
    gcalendar = GCalendar(config)
    degage = Dégage(config)

    event_registry = EventRegistry()

    # Add GCalendar events to event registry
    g_events = gcalendar.get_events()
    event_registry.update_events(g_events, google=True)

    # Add degage events to event registry
    d_events = degage.get_events()
    event_registry.update_events(d_events, degage=True)


    # Search and sync events
    for uid, e in event_registry.events.items():
        print("")
        print(f"Analyzing {uid}: {e}")
        
        # Skip sync if event has already started
        if is_started(e['start']):
            print("Skipping because event already started")
            continue

        if e['degage'] and not e['google']:
            if e['origin'] == 'degage':
                gcalendar.create_event(**e)
            else:
                degage.delete_event(e['id'])
        if not e['degage'] and e['google']:
            if e['origin'] == 'google':
                degage.create_event(**e)
            else:
                gcalendar.delete_event(e['id'])
        # when a request got accepted in degage, the [REQ]
        # in the title in gcalender is updated
        if e['recreate']:
            gcalendar.delete_event(e['id'])
            gcalendar.create_event(**e)
