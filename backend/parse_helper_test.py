import parse_helper

import consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse

kLinesWithTableOfContentsStart = \
'''# GITHUB:  NeverSinkDev

#===============================================================================================================
# [WELCOME] TABLE OF CONTENTS + QUICKJUMP TABLE
#===============================================================================================================
# [[0100]] OVERRIDE AREA 1 - Override ALL rules here
# [[0100]] Global overriding rules
# [[0200]] High tier influenced items'''

kShowHideLineIndexTestCases = [
('''Show
Sockets >= 6
Rarity <= Rare
SetFontSize 45
SetTextColor 255 255 255 255
SetBorderColor 255 255 255 255
SetBackgroundColor 59 59 59 255
PlayEffect Grey
MinimapIcon 2 Grey Hexagon''', 0),

('''# Show Desired T16 Maps
# Hide
Show
Class Maps
BaseType == "Tower Map"''', 2)]

# TODO: Add tests for remaining functions - most missing!

def TestIsSubstringInLines():
    AssertTrue(parse_helper.IsSubstringInLines(
            consts.kTableOfContentsIdentifier, kLinesWithTableOfContentsStart))
    text_lines = kLinesWithTableOfContentsStart.split('\n')
    AssertTrue(parse_helper.IsSubstringInLines(
            consts.kTableOfContentsIdentifier, text_lines))
    print('IsSubstringInLines passed!')

def TestFindShowHideLineIndex():
    for i, (rule_string, expected_index) in enumerate(kShowHideLineIndexTestCases):
        rule_lines = rule_string.split('\n') if (i % 2 == 1) else rule_string
        show_hide_line_index = parse_helper.FindShowHideLineIndex(rule_lines)
        AssertEqual(show_hide_line_index, expected_index)
    print('TestFindShowHideLineIndex passed!')

kValuesStringListTestCases = [
        ('"Orb of Chaos" "Orb of Alchemy"', ['Orb of Chaos', 'Orb of Alchemy']),
        ('Boots Gloves Helmets "Body Armours"', ['Boots', 'Gloves', 'Helmets', "Body Armours"]),
        ('"Alteration.mp3" 300', ['Alteration.mp3', '300'])]

def TestConvertValuesStringToList():
    for values_string, values_list in kValuesStringListTestCases:
        result_values_list = parse_helper.ConvertValuesStringToList(values_string)
        AssertEqual(result_values_list, values_list)
    print('TestConvertValuesStringToList passed!')

def TestConvertValuesListToString():
    for values_string, values_list in kValuesStringListTestCases:
        result_values_string = parse_helper.ConvertValuesListToString(values_list)
        AssertEqual(result_values_string, values_string)
    print('TestConvertValuesListToString passed!')

def TestParseRuleLineGeneric():
    # Standard rule line
    rule_line = '# BaseType == "Hubris Circlet" "Sorcerer\'s Gloves"'
    expected_parse_result = ('BaseType', '==', ['Hubris Circlet', "Sorcerer's Gloves"])
    AssertEqual(parse_helper.ParseRuleLineGeneric(rule_line), expected_parse_result)
    # Rule line without operator
    rule_line = 'BaseType "Splinter of Chayula" "Splinter of Uul-Netol"'
    expected_parse_result = ('BaseType', '', ['Splinter of Chayula', 'Splinter of Uul-Netol'])
    AssertEqual(parse_helper.ParseRuleLineGeneric(rule_line), expected_parse_result)
    # Strange case for Oil rules
    rule_line = '# BaseType =='
    expected_parse_result =  ('BaseType', '==', [])
    AssertEqual(parse_helper.ParseRuleLineGeneric(rule_line), expected_parse_result)
    # Keyword only
    rule_line = 'Hide'
    expected_parse_result =  ('Hide', '', [])
    AssertEqual(parse_helper.ParseRuleLineGeneric(rule_line), expected_parse_result)
    # Mixed quoted and unquoted items
    rule_line = 'CustomAlertSound "Fusing.mp3" 300 "Alteration.mp3" 200 100 "Orb of Chaos.mp3"'
    expected_parse_result = ('CustomAlertSound', '',
            ['Fusing.mp3', '300', 'Alteration.mp3', '200', '100', 'Orb of Chaos.mp3'])
    AssertEqual(parse_helper.ParseRuleLineGeneric(rule_line), expected_parse_result)
    print('TestParseRuleLineGeneric passed!')

def main():
    TestIsSubstringInLines()
    TestFindShowHideLineIndex()
    TestParseRuleLineGeneric()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()