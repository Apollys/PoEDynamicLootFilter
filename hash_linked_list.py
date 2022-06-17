class Node:
    def __init__(self, previous_node, next_node, key, value):
        self.previous_node = previous_node
        self.next_node = next_node
        self.key = key
        self.value = value
# End class Node

# Yields (key, value) pairs
class HashLinkedListIterator:
    def __init__(self, hash_linked_list):
        self.hash_linked_list = hash_linked_list
        self.current_node = hash_linked_list.head
    
    def __next__(self):
        self.current_node = self.current_node.next_node
        if (self.current_node != self.hash_linked_list.tail):
            return self.current_node.key, self.current_node.value
        raise StopIteration
# End class HashLinkedListIterator

class HashLinkedList:
    # Member variables:
    #  - self.head: Node
    #  - self.tail: Node
    #  - self.size: int
    #  - self.key_to_node_map: dict {key : node}
    def __init__(self):
        self.head = Node(None, None, None, None)
        self.tail = Node(None, None, None, None)
        self.head.next_node = self.tail
        self.tail.previous_node = self.head
        self.size = 0
        self.key_to_node_map = {}
    
    def insert_before(self, key, value, successor_key):
        next_node = (self.key_to_node_map[successor_key] if successor_key != None
                else self.tail)
        previous_node = next_node.previous_node
        new_node = Node(previous_node, next_node, key, value)
        previous_node.next_node = new_node
        next_node.previous_node = new_node
        self.key_to_node_map[key] = new_node
        self.size += 1
    
    def append(self, key, value):
        self.insert_before(key, value, successor_key=None)
    
    def __contains__(self, key) -> bool:
        return key in index_to_node_map
        
    def __iter__(self):
        return HashLinkedListIterator(self)
# End class HashLinkedList