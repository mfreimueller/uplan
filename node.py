class Node:
    def __init__(self, event, parent):
        self._event = event
        self._parent = parent
        self._children = []

        # calculate the node id
        if self.is_root():
            self._id = 0
        else:
            self._id = self._event.hash() + self._parent.id()
        
        if self.is_root():
            self.priority = 0
        else:
            self.priority = event.priority() + parent.priority
        
        if self.is_root():
            self.chance = 1
        else:
            self.chance = event.chance() * parent.chance
        
        if self.is_root():
            self.ects = 0
        else:
            self.ects = event.ects() + parent.ects
    
    def is_leaf(self):
        return len(self._children) == 0
    
    def is_root(self):
        return self._parent == None

    def id(self):
        return self._id

    def event(self):
        return self._event
    
    def parent(self):
        return self._parent
    
    def children(self):
        return self._children

    def add_node(self, child_node):
        self._children.append(child_node)
    
    def leaves(self):
        if self.is_leaf():
            if self.is_root():
                return []
            else:
                return [self]

        leaves = []

        for child in self._children:
            leaves += child.leaves()
        
        return leaves
    
    def find(self, fn):
        if self.is_root():
            return False
        
        if fn(self):
            return True
        else:
            return self._parent.find(fn)
    
    def find_child(self, fn):
        for child in self._children:
            if fn(child):
                return True
        
        return False
    
    def find_ancestor(self, fn):
        if self.is_root() or self._parent.is_root():
            return False
        
        if fn(self._parent):
            return True
        else:
            for child in self._parent._children:
                if fn(child):
                    return True
        
        return self._parent.find_ancestor(fn)

    # Insert a new node, adding all parent nodes from node, if they don't exist
    def insert(self, node):
        # first identify all parent nodes
        parent_nodes = []
        parent = node.parent()
        while not parent.is_root() and parent != None:
            parent_nodes.append(parent)
            parent = parent.parent()
        
        parent = self

        # then go in reverse and either create them or use them
        parent_nodes.reverse()
        for next_parent in parent_nodes:
            if parent.find_child(fn=lambda node: node.id() == next_parent.id()):
                parent = next_parent
            else:
                new_node = Node(next_parent.event(), parent)
                parent.add_node(new_node)

                parent = new_node
        
        # finally add a copy of node to the new parent
        node_copy = Node(node.event(), parent)
        parent.add_node(node_copy)
        