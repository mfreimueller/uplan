from event import Event
from node import Node
from node_filter import ChanceFilter, EctsFilter, IncludeFilter, PriorityFilter
import time

class Scheduler:
    def generate_schedules(self, events, max_depth, courses_to_include):
        root = Node(None, None)

        for event in events:
            node = Node(event, root)
            root.add_node(node)

            self._populate_tree_with_event(node, event, events, max_depth)

        # apply filters to cut down our tree
        filters = [ PriorityFilter(), ChanceFilter(), EctsFilter() ]

        if len(courses_to_include) > 0:
            filters.insert(0, IncludeFilter(courses_to_include))

        for filter in filters:
            if len(root.leaves()) < 10:
                break

            root = filter.apply_filter(root)

        schedules = []

        # build the schedules from the remaining leaves
        for leaf in root.leaves():
            leaf_events = [leaf.event()]
            parent = leaf.parent()
            while parent is not None and not parent.is_root():
                leaf_events.append(parent.event())
                parent = parent.parent()
            
            schedules.append(Schedule(leaf_events))

        return schedules

    def _populate_tree_with_event(self, node, event, all_events, max_depth, depth = 1):
        filtered_events = []
        for event2 in all_events:
            # remove any duplicates
            if event.id() == event2.id() or event.module_id() == event2.module_id(): # TODO: allow for similar courses from module somehow
                continue
            # remove any events that collide with `event`
            elif event.is_overlapping(event2):
                continue
            # remove any events that collide with any parent events
            elif node.find(fn=lambda n: n.event().is_overlapping(event2)):
                continue
            # remove any events that are already stored above in the tree
            elif node.find(fn=lambda n: n.event().id() == event2.id() or n.find_ancestor(fn=lambda c: c.event().id() == event2.id())):
                continue

            filtered_events.append(event2)

        schedules = []
        for event2 in filtered_events:
            new_node = Node(event2, node)
            node.add_node(new_node)

            if depth + 1 <= max_depth:
                self._populate_tree_with_event(new_node, event2, filtered_events, max_depth, depth + 1)

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