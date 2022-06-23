from item import Item

from enum import Enum
import os.path
from typing import List, Tuple

import file_helper
from loot_filter import InputFilterSource, LootFilter
import simple_parser
import test_consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse

class TestCaseBlock(Enum):
    kItemText = 0
    kItemProperties = 1
    kRuleText = 2
# End TestCaseBlock

# Parses test cases as list of triplets: item_text_string, item_properties_map, matching_rule_string
#  - item_text_string is a single string containing the item raw text
#  - item_properties_map is a dict containing the expected parsed item properties:
#     - key: str - Keyword
#     - value: str - associated value string
#  - matching_rule_string is a single string containing the matched rule raw text
def ParseTestCases(input_filepath: str) -> List[Tuple[str, dict, str]]:
    test_cases = []
    current_item_text_lines = []
    current_item_properties_map = {}
    current_rule_text_lines = []
    current_block = TestCaseBlock.kItemText
    for line in file_helper.ReadFile(input_filepath, strip=True):
        if (line == ''):
            continue
        # Start of new item text
        elif (line.startswith(test_consts.kHorizontalSeparator[:10])):
            if (len(current_item_text_lines) > 0):
                current_item_text_string = '\n'.join(current_item_text_lines)
                current_rule_text_string = '\n'.join(current_rule_text_lines)
                test_cases.append((current_item_text_string,
                        current_item_properties_map, current_rule_text_string))
            current_item_text_lines = []
            current_item_properties_map = {}
            current_rule_text_lines = []
            current_block = TestCaseBlock.kItemText
        # Start of next block within same item
        elif (line.startswith(test_consts.kHorizontalSeparatorThin[:10])):
            if (current_block == TestCaseBlock.kItemText):
                current_block = TestCaseBlock.kItemProperties
            elif (current_block == TestCaseBlock.kItemProperties):
                current_block = TestCaseBlock.kRuleText
        # Item text line
        elif (current_block == TestCaseBlock.kItemText):
            current_item_text_lines.append(line)
        # Item properties line
        elif (current_block == TestCaseBlock.kItemProperties):
            _, [keyword, value_string] = simple_parser.ParseFromTemplate(line, '{} | {}')
            current_item_properties_map[keyword] = value_string
        # Matching rule text line
        else:  # (current_block == TestCaseBlock.kRuleText)
            current_rule_text_lines.append(line)
    return test_cases

def TestParseItemText():
    test_cases = ParseTestCases(test_consts.kItemTestCasesInputFullpath)
    for item_text, expected_item_properties_map, _ in test_cases:
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