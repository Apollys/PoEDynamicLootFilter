from file_helper import WriteToFile
import file_helper

import os.path

import test_consts
import test_helper
from test_assertions import AssertEqual, AssertFailure

kTestFilepath = os.path.join(test_consts.kTestWorkingDirectory, "test_file.txt")

def TestWriteReadSimple():
    test_helper.TearDown()
    write_lines_testcases = [['Hello', 'World'], ['Hello'], ['Hello', ''], ['Hello', '', 'world']]
    for write_lines in write_lines_testcases:
        # Test write list of lines
        file_helper.WriteToFile(write_lines, kTestFilepath)
        read_lines = file_helper.ReadFile(kTestFilepath)
        AssertEqual(read_lines, write_lines)
        # Test write strings
        write_string = '\n'.join(write_lines)
        file_helper.WriteToFile(write_string, kTestFilepath)
        read_string = '\n'.join(file_helper.ReadFile(kTestFilepath))
        AssertEqual(read_string, write_string)
    print('TestWriteReadSimple passed!')

def TestWriteRead():
    test_helper.TearDown()
    write_string = "The quick brown fox\njumps\nover\n the lazy dog.\n\n"
    # Test Write and Read
    file_helper.WriteToFile(write_string, kTestFilepath)
    read_string = '\n'.join(file_helper.ReadFile(kTestFilepath))
    AssertEqual(read_string, write_string)
    test_helper.TearDown()
    print('TestWriteRead passed!')

def TestAppendRead():
    test_helper.TearDown()
    write_string = "The quick brown fox\njumps\nover\n the lazy dog.\n\n"
    # Test Append and Read
    file_helper.AppendToFile(write_string, kTestFilepath)
    read_string = '\n'.join(file_helper.ReadFile(kTestFilepath))
    AssertEqual(read_string, write_string)
    # Append more
    file_helper.AppendToFile(write_string, kTestFilepath)
    read_string = '\n'.join(file_helper.ReadFile(kTestFilepath))
    AssertEqual(read_string, 2 * write_string)
    print('TestAppendRead passed!')

def main():
    TestWriteReadSimple()
    TestWriteRead()
    TestAppendRead()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()