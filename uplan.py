from cache import store_cache, try_load_cache
from event import convert_slots_to_events, filter_events_colliding_with_slots, sort_events_by_priority
import json
from txt_exporter import TextExporter
from room import Room, load_rooms
from scheduler import Scheduler
import sys
import time
from ufind_extractor import read_course_events, read_course_ids

if len(sys.argv) < 2:
    print(".json file is required.")
    exit(1)

def read_module_ids(modules):
    module_ids = []

    for entry in modules:
        if "id" in entry:
            module_ids.append(entry["id"])

    return module_ids

try:
    json_file = open(sys.argv[1])
    json_data = json.load(json_file)
    json_file.close()
except IOError:
    print("Invalid JSON file.")
    exit(2)

module_ids = read_module_ids(json_data["modules"])
module_id_pairs = {module["id"]: module for module in json_data["modules"]}

rooms = load_rooms()

events = try_load_cache(module_ids, rooms)
if events is None:
    def read_all_events(module_ids):
        all_events = []

        for module_id in module_ids:
            course_ids = read_course_ids(module_id)
            for course_id in course_ids:
                events = read_course_events(course_id, module_id_pairs[module_id], json_data["priorities"])
                all_events.extend(events)
                time.sleep(0.5) # prevent firing too many calls in too short of a time

            time.sleep(1) # prevent firing too many calls in too short of a time

        return all_events

    print("Reading events of modules...")
    events = read_all_events(module_ids)

    store_cache(module_ids, events)
    print("Finished reading events of modules...")

    print("Please clean up data and start again.")

    exit(0)

mandatory_courses = []
# we can append all course ids that we want to have in our plan
if len(sys.argv) > 2:
    for idx in range(2, len(sys.argv)):
        mandatory_courses.append(sys.argv[idx])

slots = convert_slots_to_events(json_data["unavailable_slots"])

filtered_events = filter_events_colliding_with_slots(events, slots)
filtered_events = sort_events_by_priority(filtered_events, json_data["modules"])

scheduler = Scheduler(mandatory_courses)
schedules = scheduler.generate_schedules(filtered_events, 9)

text_exporter = TextExporter()
print(text_exporter.export_schedules(schedules))