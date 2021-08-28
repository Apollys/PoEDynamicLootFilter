'''
Defines a very simple multiset class for Python 3.
'''

class Multiset:
    '''
    Stores the given items in a dictionary mapping values to counts.
    
    Member variables:
     - self.count_dict
     - self.value_list - list representing the multiset, updated lazily
    '''
    
    def __init__(self, iterable_container):
        self.count_dict = {}
        self.value_list = []
        for value in iterable_container:
            if (value in self.count_dict):
                self.count_dict[value] += 1
            else:
                self.count_dict[value] = 1
    
    def insert(self, value):
        if (value in self.count_dict):
            self.count_dict[value] += 1
        else:
            self.count_dict[value] = 1
    
    # Removes one instance of given value, if it exists in the set
    def remove(self, value):
        if (value in self.count_dict):
            self.count_dict[value] -= 1
            if (self.count_dict[value] == 0):
                self.count_dict.pop(value)
                
    def count(self, value):
        return self.count_dict[value] if value in self.count_dict else 0
    
    # not_eq will automatically be defined if eq is defined in Python3
    def __eq__(self, other):
        if isinstance(other, multiset):
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
        self.value_list = []
        for value, count in self.count_dict.items():
            self.value_list.extend([value for i in range(count)])

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

