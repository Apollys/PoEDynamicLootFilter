from hash_linked_list import HashLinkedList

from test_assertions import AssertEqual, AssertFailure

def SimpleTest():
    # Build HashLinkedList mapping int keys to their corresponding strings as values
    hll = HashLinkedList()
    hll.append(4, '4')
    hll.append(7, '7')
    hll.insert_before(6, '6', 7)
    hll.insert_before(8, '8', None)
    hll.insert_after(5, '5', 4)
    hll.insert_after(3, '3', None)
    # Create reference key list
    expected_key_list = list(range(3, 9))
    # Verify the HashLinkedList matches the reference list
    for i, (key, value) in enumerate(hll):
        expected_key = expected_key_list[i]
        expected_value = str(expected_key)
        AssertEqual(expected_key, key)
        AssertEqual(expected_value, value)
    AssertEqual(hll.size, len(expected_key_list))
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
    AssertEqual(hll.size, len(reference_key_list))
    print('LargerTest passed!')

def TestInsertAtIndex():
    hll = HashLinkedList()
    for i in range(10):
        hll.append(i, str(i))
    hll.insert_at_index(-1, '-1', 0)
    hll.insert_at_index(11, '11', 11)
    hll.insert_at_index(12, '12', 100)
    reference_key_list = list(range(-1, 10)) + [11, 12]
    # Verify the HashLinkedList matches the reference list
    for i, (key, value) in enumerate(hll):
        expected_key = reference_key_list[i]
        expected_value = str(expected_key)
        AssertEqual(expected_key, key)
        AssertEqual(expected_value, value)
    AssertEqual(hll.size, len(reference_key_list))
    print('TestInsertAtIndex passed!')

def TestBracketAccess():
    hll = HashLinkedList()
    for key in range(10):
        hll.append(key, str(key))
    AssertEqual(hll[5], str(5))
    hll[5] = 'five'
    AssertEqual(hll[5], 'five')
    # Expect error when trying to set value whose key is missing
    try:
        hll[-1] = 'x'
    except KeyError:  # this should happen
        pass
    else:
        AssertFailure()
    print('TestBracketAccess passed!')

def main():
    SimpleTest()
    LargerTest()
    TestInsertAtIndex()
    TestBracketAccess()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()