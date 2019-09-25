

class EventRegistry:
    def __init__(self):
        self.events = {}
    
    def update_event(self, start, end, summary, description, google=False, degage=False, id='', origin='google'):
        """ Add or update event to Events """
        uid = f'{start}---{end}'
        if uid in self.events:
            self.events[uid]['google'] = self.events[uid]['google'] or google
            self.events[uid]['degage'] = self.events[uid]['degage'] or degage

            # detect if car request got accepted to update status in gcalendar
            # this happens when in google Calendar there is [REG] in the name
            # while not anymore in degage. Since Google is fetched first, we
            # can check this case
            if "[REQ]" in self.events[uid]['summary'] and "[REQ]" not in summary:
                self.events[uid]['summary'] = summary
                self.events[uid]['recreate'] = True
        else:
            self.events[uid] = {
                'id': id,
                'summary': summary,
                'description': description,
                'start': start,
                'end': end,
                'google': google,
                'degage': degage,
                'origin': origin,
                'recreate': False
                            }

    def update_events(self, events, google=False, degage=False):
        for event in events:
            self.update_event(**event, google=google, degage=degage)