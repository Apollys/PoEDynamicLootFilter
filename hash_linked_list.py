class HllNode:
    def __init__(self, previous_node, next_node, key, value):
        self.previous_node = previous_node
        self.next_node = next_node
        self.key = key
        self.value = value
# End class HllNode

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
    #  - self.head: HllNode
    #  - self.tail: HllNode
    #  - self.size: int
    #  - self.key_to_node_map: dict {key : node}
    def __init__(self):
        self.head = HllNode(None, None, None, None)
        self.tail = HllNode(None, None, None, None)
        self.head.next_node = self.tail
        self.tail.previous_node = self.head
        self.size = 0
        self.key_to_node_map = {}
    
    # A successor_key of None indicates to insert at the end
    def insert_before(self, key, value, successor_key):
        next_node = (self.key_to_node_map[successor_key] if successor_key != None
                else self.tail)
        previous_node = next_node.previous_node
        new_node = HllNode(previous_node, next_node, key, value)
        previous_node.next_node = new_node
        next_node.previous_node = new_node
        self.key_to_node_map[key] = new_node
        self.size += 1
    
    # A predecessor_key of None indicates to insert at the beginning
    def insert_after(self, key, value, predecessor_key):
        previous_node = (self.key_to_node_map[predecessor_key] if predecessor_key != None
                else self.head)
        self.insert_before(key, value, previous_node.next_node.key)
    
    # Time complexity: O(index)
    # If index > size, appends to the end of the list.
    def insert_at_index(self, key, value, index: int):
        # Get nth item of iterator: https://stackoverflow.com/a/54333239
        successor_key, _ = next((x for i, x in enumerate(self) if i==index), (None, None))
        self.insert_before(key, value, successor_key)
    
    def append(self, key, value):
        self.insert_before(key, value, successor_key=None)
    
    def get_node(self, key):
        return self.key_to_node_map[key]
    
    def __contains__(self, key) -> bool:
        return key in self.key_to_node_map
    
    def __getitem__(self, key):
        return self.key_to_node_map[key].value
    
    # Only to be used for changing the value of an existing node.
    # If node with specified key does not exist, raises a KeyError.
    def __setitem__(self, key, value):
        self.key_to_node_map[key].value = value
        
    def __iter__(self):
        return HashLinkedListIterator(self)
# End class HashLinkedList