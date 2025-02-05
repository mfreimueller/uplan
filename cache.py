from datetime import datetime
from event import Event
import json

def store_cache(module_ids, events):
    data = {
        "ts": datetime.timestamp(datetime.now()),
        "module_ids": module_ids,
        "events": events
    }

    cache_file = open(".cache", "w")
    json.dump(data, cache_file)
    cache_file.close()

# Attempts to load a .cache file, if the following 
# constraints are fulfilled:
# 1. the module_ids provided as parameters match 
# 2. the timestamp is within a 24 hours bound
def try_load_cache(module_ids, rooms):
    try:
        cache_file = open(".cache", "r")
        cache_data = json.load(cache_file)
        cache_file.close()
    except IOError:
        return None

    if "ts" not in cache_data or "module_ids" not in cache_data or "events" not in cache_data:
        return None

    # first calculate the difference in days
    cache_dt = datetime.fromtimestamp(cache_data["ts"])
    now_dt = datetime.now()

    if (now_dt - cache_dt).days > 2:
        return None

    # then compare the module ids
    cache_module_ids = cache_data["module_ids"]

    if len(module_ids) != len(cache_module_ids):
        return None

    module_ids.sort()
    cache_module_ids.sort()

    for idx in range(len(module_ids)):
        if module_ids[idx] != cache_module_ids[idx]:
            return None

    # if the timestamp is within the allowed bounds and
    # all modules match, we convert the stored events into objects
    events = []

    for event in cache_data["events"]:
        events.append(Event(event, rooms[event["room"]]))

    return events