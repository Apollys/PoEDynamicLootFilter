from multiset import Multiset

from test_assertions import AssertEqual, AssertFailure

def TestConstructInsertRemoveLen():
    # Initialize multiset from 2 copies of each integer in [0, 10)
    m = Multiset(2 * list(range(10)))
    m.remove(5)
    m.insert(11)
    m.insert(11)
    m.insert(11)
    AssertEqual(m.count(0), 2)
    AssertEqual(m.count(5), 1)
    AssertEqual(m.count(11), 3)
    expected_count_dict = {i: 2 for i in range(10)}
    expected_count_dict[5] = 1
    expected_count_dict[11] = 3
    AssertEqual(m.count_dict, expected_count_dict)
    AssertEqual(len(m), sum(count for count in expected_count_dict.values()))
    print('TestConstructInsertRemoveLen passed!')

# If values are only inserted, never deleted, the order of elements
# received when iterating through the container should be deterministic.
def TestDeterministicOrder():
    input_values = list(range(1000)) + 10 * list(range(10)) + list(range(1000000))
    m1 = Multiset(input_values)
    m2 = Multiset(input_values)
    for i in range(100000):
        m1.insert(3 * i)
        m2.insert(3 * i)
    AssertEqual(list(m1), list(m2))
    print('TestDeterministicOrder passed!')
    

def main():
    TestConstructInsertRemoveLen()
    TestDeterministicOrder()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()