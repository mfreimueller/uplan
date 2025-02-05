from room import Room

class Event:
    _data = {}
    _room = None

    start_hour = None
    start_minute = None

    end_hour = None
    end_minute = None

    def __init__(self, event, room):
        self._data = event
        self._room = room

        if "start" in event:
            self.start_hour = int(event["start"][:2])
            self.start_minute = int(event["start"][-2:])

            self.end_hour = int(event["end"][:2])
            self.end_minute = int(event["end"][-2:])

    def __str__(self):
        return f"{self.title}({self.id})"
    
    def id(self):
        return self._data["id"]

    def day(self):
        return self._data["day"]

    def module_id(self):
        return self._data["module_id"]

    def title(self):
        return self._data["title"]

    def priority(self):
        return self._data["priority"]
    
    def chance(self):
        return self._data["chance"]
    
    def ects(self):
        return self._data["ects"]

    def full_hour(self):
        if self.start_hour is None:
            return None

        start_hour = self.start_hour
        if self.start_minute >= 30:
            start_hour += 1
        
        if start_hour < 10:
            return "0" + str(start_hour) + ":00"
        else:
            return str(start_hour) + ":00"

    def date_format(self):
        return self._data["start"] + " - " + self._data["end"]
    
    def number_of_hours(self):
        return self.end_hour - self.start_hour

    def is_overlapping(self, event):
        if self.day() != event.day():
            return False

        if event.start_hour is None or self.start_hour is None:
            return True

        events = []
        if self.start_hour < event.start_hour or (self.start_hour == event.start_hour and self.start_minute < event.start_minute):
            events = [self, event]
        else:
            events = [event, self]
        
        end_ts = events[0].end_hour * 60 + events[0].end_minute
        start_ts = events[1].start_hour * 60 + events[1].start_minute

        # if the first course ends after the second begins, they overlap
        if end_ts > start_ts:
            return True

        # skip travel time is one of the events has no room assigned
        if events[0]._room is None or events[1]._room is None:
            return False
        
        room_delay = events[0]._room.get_travel_time(events[1]._room)

        # if there is not enough space between the two courses for travel, they overlap
        if (start_ts - end_ts) < room_delay:
            return True
        
        return True

def convert_slots_to_events(slots):
    converted_slots = []

    for slot in slots:
        if "start" not in slot:
            continue

        converted_slots.append(Event(slot, None))
    
    return converted_slots

# Filter all events that are colliding with blocked slots, leaving
# only those events that can be taken on.
def filter_events_colliding_with_slots(events, slots):
    # now we want to filter out all events clashing with our unavailable slots
    filtered_events = []
    for event in events:
        blocked = False
        for slot in slots:
            if slot.is_overlapping(event):
                blocked = True
                break
        
        if not blocked:
            filtered_events.append(event)

    return filtered_events

# Sort a list of events based on their assigned modules priority.
def sort_events_by_priority(events, modules):
    module_priorities = {module["id"]: module["priority"] for module in modules}
    return sorted(events, key=lambda event: module_priorities[event.module_id()])