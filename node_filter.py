from node import Node

# A filter that filters out all leaves that don't include
# a list of courses.
class IncludeFilter:
    def __init__(self, courses):
        self._courses = courses

    def apply_filter(self, tree):
        # first retrieve all leaves of the tree
        leaves = tree.leaves()
        
        new_tree = Node(None, None)
        for leaf in leaves:
            misses_course = False
            for course in self._courses:
                course_id = course[:-2] if course.find(":") != -1 else course
                group_name = course[-1] if course.find(":") != -1 else "1"

                if not leaf.find(fn=lambda node: (node.event().id() == course_id and node.event().group_name() == group_name) or node.event().module_id() == course_id):
                    misses_course = True
                    break
            
            if not misses_course:
                new_tree.insert(leaf)

        print("[IncludeFilter] Reduced", len(leaves), "number of leaves to", len(new_tree.leaves()))

        return new_tree

# A filter that filters out all leaves whose priority lies below the average.
class PriorityFilter:
    def apply_filter(self, tree):
        # first retrieve all leaves of the tree
        leaves = tree.leaves()

        # then sort them by their priority
        leaves = sorted(leaves, key=lambda leaf: leaf.priority, reverse=True)

        total_priority = sum(leaf.priority for leaf in leaves)
        average = total_priority / len(leaves)

        print("[PriorityFilter] Average priority:", average)

        new_tree = Node(None, None)
        for leaf in leaves:
            if leaf.priority >= average:
                new_tree.insert(leaf)
        
        print("[PriorityFilter] Reduced", len(leaves), "number of leaves to", len(new_tree.leaves()))

        return new_tree

# A filter that filters out all leaves whose chance lies below the average.
class ChanceFilter:
    def apply_filter(self, tree):
        # first retrieve all leaves of the tree
        leaves = tree.leaves()

        # then sort them by their priority
        leaves = sorted(leaves, key=lambda leaf: leaf.chance, reverse=True)

        total_chance = sum(leaf.chance for leaf in leaves)
        average = total_chance / len(leaves)

        print("[ChanceFilter] Average chance:", average)

        new_tree = Node(None, None)
        for leaf in leaves:
            if leaf.chance >= average:
                new_tree.insert(leaf)
        
        print("[ChanceFilter] Reduced", len(leaves), "number of leaves to", len(new_tree.leaves()))

        return new_tree

# A filter that filters out all leaves whose ECTS lie below the average.
class EctsFilter:
    def apply_filter(self, tree):
        # first retrieve all leaves of the tree
        leaves = tree.leaves()

        # then sort them by their priority
        leaves = sorted(leaves, key=lambda leaf: leaf.ects, reverse=True)

        total_ects = sum(leaf.ects for leaf in leaves)
        average = int(total_ects / len(leaves))

        print("[EctsFilter] Average ECTS:", average)

        new_tree = Node(None, None)
        for leaf in leaves:
            if leaf.ects >= average:
                new_tree.insert(leaf)
        
        print("[EctsFilter] Reduced", len(leaves), "number of leaves to", len(new_tree.leaves()))

        return new_tree