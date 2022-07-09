import string_helper

from test_assertions import AssertEqual, AssertTrue, AssertFalse, AssertFailure

def TestToTitleCase():
    AssertEqual(string_helper.ToTitleCase('hello world'), 'Hello World')
    AssertEqual(string_helper.ToTitleCase('hello-world'), 'Hello-World')
    AssertEqual(string_helper.ToTitleCase('DLF = dynamic loot filter'), 'DLF = Dynamic Loot Filter')
    AssertEqual(string_helper.ToTitleCase("The fox's rival"), "The Fox's Rival")
    print('TestToTitleCase passed!')

def main():
    TestToTitleCase()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()