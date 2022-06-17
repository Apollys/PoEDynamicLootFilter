from hash_linked_list import HashLinkedList
from test_helper import AssertEqual

def SimpleTest():
    # Build HashLinkedList mapping int keys to their corresponding strings as values
    hll = HashLinkedList()
    hll.append(5, '5')
    hll.append(7, '7')
    hll.insert_before(6, '6', 7)
    hll.insert_before(4, '4', 5)
    # Create reference key list
    expected_key_list = [4, 5, 6, 7]
    # Verify the HashLinkedList matches the reference list
    for i, (key, value) in enumerate(hll):
        expected_key = expected_key_list[i]
        expected_value = str(expected_key)
        AssertEqual(expected_key, key)
        AssertEqual(expected_value, value)
    print('SimpleTest passed!')

def LargerTest():
    # Build HashLinkedList mapping int keys to their corresponding strings as values
    num_items = 1000
    hll = HashLinkedList()
    for key in range(num_items):
        hll.append(key, str(key))
    for successor_key in range(num_items):
        hll.insert_before(-1, str(-1), successor_key)
    # Build equivalent list for reference
    reference_key_list = list(range(num_items))
    for successor_key in range(num_items):
        successor_index = reference_key_list.index(successor_key)
        reference_key_list.insert(successor_index, -1)
    # Verify the HashLinkedList matches the reference list
    for i, (key, value) in enumerate(hll):
        expected_key = reference_key_list[i]
        expected_value = str(expected_key)
        AssertEqual(expected_key, key)
        AssertEqual(expected_value, value)
    print('LargerTest passed!')

def BracketAccessTest():
    hll = HashLinkedList()
    for key in range(10):
        hll.append(key, str(key))
    AssertEqual(hll[5], str(5))
    hll[5] = 'five'
    AssertEqual(hll[5], 'five')
    print('BracketAccessTest passed!')

def main():
    SimpleTest()
    LargerTest()
    BracketAccessTest()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()