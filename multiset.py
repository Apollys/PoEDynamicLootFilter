'''
Defines a very simple multiset class for Python 3.
'''

class Multiset:
    '''
    Stores the given items in a dictionary mapping values to counts.
    
    Member variables:
     - self.count_dict: dict mapping value to count
     - self.value_list: list containing the values in the multiset
        - value_list is used for __repr__ and instantiated in such
          a way that if items are never removed from the multiset,
          __repr__ always lists the items in order of insertion.
     - self.value_list_outdated: bool
    '''
    
    def __init__(self, iterable_container):
        self.count_dict = {}
        self.value_list = []
        self.value_list_outdated = False
        for value in iterable_container:
            self.insert(value)
    
    def insert(self, value):
        if (value in self.count_dict):
            self.count_dict[value] += 1
        else:
            self.count_dict[value] = 1
        self.value_list.append(value)
    
    # Removes one instance of given value, if it exists in the set
    def remove(self, value):
        if (value in self.count_dict):
            self.count_dict[value] -= 1
            if (self.count_dict[value] == 0):
                self.count_dict.pop(value)
            self.value_list_outdated = True

    def count(self, value):
        return self.count_dict.get(value, 0)
    
    # Note: __not_eq__ will automatically be defined if __eq__ is defined in Python3
    def __eq__(self, other):
        if isinstance(other, Multiset):
            return self.count_dict == other.count_dict
        return False
        
    def __contains__(self, value):
        return value in self.count_dict
        
    def __len__(self):
        self._update_value_list()
        return len(self.value_list)
    
    def __iter__(self):
        self._update_value_list()
        return iter(self.value_list)
        
    def __repr__(self):
        self._update_value_list()
        if (len(self.value_list) == 0):
            return '{}'
        s = '{'
        for value in self.value_list:
            s += repr(value) + ', '
        return s[: -2] + '}'
        
    def _update_value_list(self):
        if (not self.value_list_outdated):
            return
        self.value_list = []
        for value, count in self.count_dict.items():
            self.value_list.extend([value for i in range(count)])
        self.value_list_outdated = False

def Test():
    m = Multiset(['r', 'r', 'g', 'a', 'r'])
    print(m)
    m.remove('r')
    print(m)
    m.insert('b')
    print(m)
    m.insert('a')
    print(m)
    # Iterator test
    print([x for x in m])
    
#Test()

