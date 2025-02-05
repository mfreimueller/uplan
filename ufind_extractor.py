import requests

def extract_module_name(content: str):
    div_idx = content.find("usse-id-vvz")
    if div_idx == -1:
        return None
    
    h1_idx = content.find("<h1>", div_idx)
    if h1_idx != -1:
        h1_tag = ""
        for idx in range(h1_idx + 4, len(content)):
            if content[idx] == "<":
                break

            h1_tag += content[idx]

        h1_tag = h1_tag.strip()
        return h1_tag
    return None

def read_course_ids(module_id):
    response = requests.get("https://ufind.univie.ac.at/de/vvz_sub.html?path=" + module_id)
    content = response.text

    # read the h1 tag to print out
    module_name = extract_module_name(content) or "Unknown"
    print("Beginning scan of", module_name, "...")

    next_course_idx = content.find("course.html?lv=")

    course_ids = []
    while next_course_idx != -1:
        idx = next_course_idx + 15

        course_id = ""
        while idx < len(content):
            if content[idx].isnumeric():
                course_id += content[idx]
                idx += 1
            else:
                break
        
        course_ids.append(course_id)
        next_course_idx = content.find("course.html?lv=", next_course_idx + 1)
    
    print("Finished scan of", module_name, "...")

    return course_ids

def read_course_events(course_id, module, priorities):
    print("Beginning extraction of events from", course_id, "...")
    
    response = requests.get("https://ufind.univie.ac.at/de/course.html?lv=" + course_id + "&semester=2025S")
    content = response.text

    title_idx = content.find("what", content.find("title") + 1)
    title = content[title_idx + 6 : content.find("<", title_idx)]

    print("[", title, "]")

    events = []

    group_idx = content.find("usse-id-group")

    group_counter = 1
    while group_idx != -1:
        event_line_idx = content.find("event line", group_idx)

        # some lecturers seem to be unable to provide the correct format.
        day_idx = content.find("day", event_line_idx)
        if day_idx == -1:
            day = None
        else:
            day = content[day_idx + 5 : content.find("<", day_idx)]

        time_idx = content.find("time", event_line_idx)
        if time_idx == -1:
            time = None
        else:
            time = content[time_idx + 6 : content.find("<", time_idx)]

        room_idx = content.find("room", event_line_idx)
        if room_idx == -1:
            room = None
        else:
            room = content[room_idx + 6 : content.find("<", room_idx)]

            # extract the locations of the course
            if room.find("Währinger Straße") != -1:
                room = "Währinger Straße"
            elif room.find("Lehr-Lern-Labor EDEN") != -1:
                room = "Lehr-Lern-Labor EDEN"
            elif room.find("NIG") != -1:
                room = "NIG"
            elif room.find("Hauptgebäude") != -1:
                room = "Hauptgebäude"
            elif room.find("Grenzackerstraße") != -1:
                room = "Grenzackerstraße"
            elif room.find("Porzellangasse") != -1:
                room = "Porzellangasse"
            elif room.find("UniCampus") != -1:
                room = "UniCampus"
            elif room.find("Baden") != -1:
                room = "Baden"
            elif room.find("Ettenreichgasse") != -1:
                room = "Ettenreichgasse"
            elif room.find("Kolingasse") != -1:
                room = "Kolingasse"
            elif room.find("Sensengasse") != -1:
                room = "Sensengasse"
            elif room.find("Postgasse") != -1:
                room = "Postgasse"
            else:
                print("Unknown room for", id, "(", title, "): ", room)
                room = "UNKNOWN"
        
        max_idx = content.find("\"n\"", content.find("class=\"max\""))
        if max_idx == -1:
            max = None
        else:
            max = int(content[max_idx + 4 : content.find("<", max_idx)])
        
        ects_idx = content.find("ects\"")
        if ects_idx == -1:
            ects = None
        else:
            ects = int(float(content[ects_idx + 6 : content.find("<", ects_idx)]))

        participants = module["participants"] if "participants" in module else None

        has_priority = False
        for prio_course in priorities:
            if prio_course["course_id"] == course_id:
                if "group_name" not in prio_course or prio_course["group_name"] == str(group_counter):
                    has_priority = True
                    break

        events.append({
            "id": course_id,
            "title": title,
            "group_name": str(group_counter),
            "day": day,
            "start": None if time is None else time[:5],
            "end": None if time is None else time[-5:],
            "module_id": module["id"],
            "chance": None if max is None or participants is None else (max / participants),
            "priority": module["priority"] if has_priority else (module["priority"] / 2),
            "room": room,
            "ects": ects
        })

        group_counter += 1
        group_idx = content.find("usse-id-group", group_idx + 1)

    print("Finished extraction of events from", title, "...")

    return events