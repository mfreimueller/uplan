import json

class Room:
    _name = ""
    _costs = {}

    def __init__(self, name, json_data):
        self._name = name
        self._costs = json_data
    
    def get_travel_time(self, room):
        room_pair = [self, room]
        room_pair.sort(key=lambda x: x._name)

        return room_pair[0]._costs[room_pair[1]._name]

def load_rooms():
    rooms_file = open("rooms.json")
    rooms_json = json.load(rooms_file)
    rooms_file.close()

    rooms = {
        "UNKNOWN": None
    }
    for room_key in rooms_json.keys():
        rooms[room_key] = Room(room_key, rooms_json[room_key])

    return rooms