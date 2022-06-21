from item import Item

import os.path
from typing import List, Tuple

import file_helper
from loot_filter import InputFilterSource, LootFilter
import profile
import simple_parser
import test_consts
from test_helper import AssertEqual, AssertTrue, AssertFalse

kTestCasesFilename = 'item_test_cases_verified.txt'
kTestCasesFullpath = os.path.join(test_consts.kTestResourcesDirectory, kTestCasesFilename)

kHorizontalSeparator = \
        '================================================================================'
kHorizontalSeparatorThin = \
        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

# Parses test cases as list of pairs: item_text_string, item_properties_map
#  - item_text_string is a single string containing the item raw text
#  - item_properties_map is a dict containing the expected parsed item properties:
#     - key: str - Keyword
#     - value: str - associated value string
def ParseTestCases(input_filepath: str) -> List[Tuple[str, dict]]:
    test_cases = []
    current_item_text_lines = []
    current_item_properties_map = {}
    in_properties_flag = False
    for line in file_helper.ReadFile(input_filepath, strip=True):
        if (line == ''):
            continue
        # Start of new item text
        elif (line.startswith(kHorizontalSeparator[:10])):
            if (len(current_item_text_lines) > 0):
                current_item_text_string = '\n'.join(current_item_text_lines)
                test_cases.append((current_item_text_string, current_item_properties_map))
            current_item_text_lines = []
            current_item_properties_map = {}
            in_properties_flag = False
        # Start of parsed item properties
        elif (line.startswith(kHorizontalSeparatorThin[:10])):
            in_properties_flag = True
        elif (not in_properties_flag):
            current_item_text_lines.append(line)
        else:  # if (in_properties_flag)
            _, [keyword, value_string] = simple_parser.ParseFromTemplate(line, '{} | {}')
            current_item_properties_map[keyword] = value_string
    return test_cases

def TestParseItemText():
    test_cases = ParseTestCases(kTestCasesFullpath)
    for item_text, expected_item_properties_map in test_cases:
        item = Item(item_text)
        # Compare item.properties_map and expected_item_properties_map:
        # Keys should be equal, values should be string-equal
        AssertEqual(set(item.properties_map.keys()), set(expected_item_properties_map.keys()))
        for keyword in item.properties_map:
            AssertEqual(str(item.properties_map[keyword]), expected_item_properties_map[keyword])
    print('TestParseItemText passed!')

def main():
    TestParseItemText()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()