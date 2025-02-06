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
elif len(sys.argv) < 3:
    print("Maximum number of courses required.")
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

maximum_number_courses = int(sys.argv[2])

mandatory_courses = []
# we can append all course ids that we want to have in our plan
if len(sys.argv) > 3:
    for idx in range(3, len(sys.argv)):
        mandatory_courses.append(sys.argv[idx])

slots = convert_slots_to_events(json_data["unavailable_slots"])

filtered_events = filter_events_colliding_with_slots(events, slots)
filtered_events = sort_events_by_priority(filtered_events, json_data["modules"])

courses_to_include = []
courses_to_exclude = []

for course in mandatory_courses:
    if course.startswith("-"):
        courses_to_exclude.append(course[1:])
    else:
        if course.startswith("+"):
            courses_to_include.append(course[1:])
        else:
            courses_to_include.append(course)

for course in courses_to_exclude:
    course_id = course[:-2] if course.find(":") != -1 else course
    group_name = course[-1] if course.find(":") != -1 else "1"
    
    courses_without_excluded = []
    for event in filtered_events:
        if (event.id() == course_id and event.group_name() == group_name):
            continue
        elif event.module_id() == course_id:
            continue
        
        courses_without_excluded.append(event)
        
    filtered_events = courses_without_excluded

schedules = Scheduler().generate_schedules(filtered_events, maximum_number_courses, courses_to_include)

text_exporter = TextExporter()
txt = text_exporter.export_schedules(schedules)

out_file = open("plan.txt", "w")
out_file.write(txt)
out_file.close()