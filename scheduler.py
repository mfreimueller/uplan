from event import Event
from weight import MultiplicationWeightCalculator
import threading
import time

class Scheduler:
    _weightCalculator = MultiplicationWeightCalculator()
    _mandatory_courses = []

    _generated_schedules_hashes = []
    _generated_schedules = []

    def __init__(self, mandatory_courses):
        self._mandatory_courses = mandatory_courses
        self._lock = threading.Lock()

    def generate_schedules(self, events, max_depth):
        threads = []
        for event in events:
            event_thread = threading.Thread(target=self._create_and_filter_schedules, args=(event, events, max_depth))
            event_thread.start()
            threads.append(event_thread)
        
        for thread in threads:
            thread.join()

        # now that we generated a list of plausible candidates, we sort them by their ECTS and the chance thereof
        self._generated_schedules.sort(key=lambda x: x.ects() * x.total_chance() * len(x.events()), reverse=True)

        return self._generated_schedules[:10]

    def _create_and_filter_schedules(self, event, events, max_depth):
        schedules = self._create_schedules_for_event(event, events, max_depth)

        generated_schedules_hashes = []
        generated_schedules = []

        for idx in range(len(schedules)):
            # as duplications are possible, we filter any schedules we already processed
            hash = 0
            for idx1 in range(1, len(schedules[idx])):
                hash += schedules[idx][idx1].hash()
            
            if hash not in generated_schedules_hashes:
                generated_schedules_hashes.append(hash)

                # before we continue, we want to make sure that all mandatory courses are in this schedule
                must_exclude = False
                for course in self._mandatory_courses:
                    # if a course id is prefixed with + or - we must in- or exclude it
                    course_id = course[1:] if course.startswith("+") or course.startswith("-") else course
                    course_to_exclude = course.startswith("-")
                    group_name = "1"
                    
                    if course.find(":") != -1:
                        group_name = course_id[-1]
                        course_id = course[:-2]

                    found_course = False
                    for idx2 in range(1, len(schedules[idx])):
                        event = schedules[idx][idx2]
                        if event.id() == course_id and event.group_name() == group_name:
                            found_course = True
                            break
                    
                    if course_to_exclude and found_course:
                        must_exclude = True
                        break
                    elif not course_to_exclude and not found_course:
                        must_exclude = True
                        break
                
                if not must_exclude:
                    # [1:] to skip the calculated chance at index 0
                    generated_schedules.append(Schedule(schedules[idx][1:]))
        
        # we are done with filtering the usable schedules. Now we need to add them to the global pool
        while not self._lock.acquire(blocking=False):
            time.sleep(1)
            
        for schedule in generated_schedules:
            if schedule.hash() not in self._generated_schedules_hashes:
                self._generated_schedules_hashes.append(schedule.hash())
                self._generated_schedules.append(schedule)

        self._lock.release()

    def _create_schedules_for_event(self, event, all_events, max_depth, parents = [], depth = 1, parent_weight = 0):
        if depth > max_depth:
            return []

        filtered_events = []
        for event2 in all_events:
            if event.id() == event2.id() or event.module_id() == event2.module_id():
                continue
            elif event.is_overlapping(event2):
                continue
            
            colliding = False
            for parent in parents:
                if event2.is_overlapping(parent):
                    colliding = True
                    break

            if not colliding:
                filtered_events.append(event2)

        self_weight = parent_weight + (event.chance() * event.priority())

        schedules = []
        for event2 in filtered_events:
            generated_schedules = self._create_schedules_for_event(event2, filtered_events, max_depth, parents + [event], depth + 1, self_weight)

            for schedule in generated_schedules:
                schedule.append(event)

                # if we are back in the first layer, we add the depth of the schedule
                # to the weight
                if depth == 1:
                    schedule[0] = schedule[0] * (len(schedule) - 1) / max_depth

                schedules.append(schedule)

        if len(schedules) == 0:
            return [[self_weight, event]]
        else:
            return schedules


class Schedule:
    _events = []
    _ects = 0
    _total_chance = 1

    def __init__(self, events):
        self._events = sorted(events, key=sort_events)

        for idx in range(1, len(events)):
            event = events[idx]

            self._ects += event.ects()
            self._total_chance *= event.chance()

        self._hash = 0
        for event in events:
            self._hash += event.hash()

    def hash(self):
        return self._hash

    def events(self):
        return self._events

    def ects(self):
        return self._ects
    
    def total_chance(self):
        return self._total_chance

# A helper function that returns the timestamp of an event
# in minutes.
def sort_events(event):
    start_ts = (event.start_hour * 60) + event.start_minute

    if event.day() == "Montag":
        return start_ts
    elif event.day() == "Dienstag":
        return start_ts + 1440
    elif event.day() == "Mittwoch":
        return start_ts + 2880
    elif event.day() == "Donnerstag":
        return start_ts + 4320
    elif event.day() == "Freitag":
        return start_ts + 5760
    elif event.day() == "Samstag":
        return start_ts + 7200
    else:
        return start_ts + 8640