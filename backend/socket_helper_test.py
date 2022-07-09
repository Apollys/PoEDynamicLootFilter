import socket_helper
import string_helper

from test_assertions import AssertEqual, AssertTrue, AssertFalse, AssertFailure

# List of (socket_string, item_slot, normalized_socket_string, tier_tag, rule_condition_lines)
kSocketStringTestCases = [
    ('XX X XXX', 'any', 'X X X X X X', 'x_x_x_x_x_x__any', ['Sockets >= 6']),
    ('R-G-B', 'helmets', 'R-G-B', 'r-g-b__helmets', ['Class "Helmets"', 'Sockets >= 3RGB', 'SocketGroup >= 3RGB']),
    ('x-x-x', 'boots', 'X-X-X', 'x-x-x__boots', ['Class "Boots"', 'Sockets >= 3', 'SocketGroup >= 3']),
    ('R-r-r G-g B', 'any', 'R-R-R G-G B', 'r-r-r_g-g_b__any',
            ['Sockets >= 6RRRGGB', 'SocketGroup >= 3RRR', 'SocketGroup >= 2GG']),
    ('X-rA-x-D-w', 'Body Armours', 'X-R A-X-D-W', 'x-r_a-x-d-w__body_armours',
            ['Class "Body Armours"', 'Sockets >= 6RADW', 'SocketGroup >= 2R', 'SocketGroup >= 4ADW']),
    ('r-g-x-x b-x', 'Weapons', 'R-G-X-X B-X', 'r-g-x-x_b-x__weapons',
            ['Class "Weapons"', 'Sockets >= 6RGB', 'SocketGroup >= 4RG', 'SocketGroup >= 2B']),
]

kInvalidSocketStrings = [
    'ABC',
    'R--G',
    'R-B-G-',
    'R B G ',
    '-W',
    '-',
]

def TestNormalizeSocketString():
    for socket_string, _, expected_normalized_socket_string, _, _ in kSocketStringTestCases:
        normalized_socket_string = socket_helper.NormalizedSocketString(socket_string)
        AssertEqual(normalized_socket_string, expected_normalized_socket_string)
    print('TestNormalizeSocketString passed!')

def TestGenerateDecodeTierTag():
    for socket_string, item_slot, normalized_socket_string, tier_tag, _ in kSocketStringTestCases:
        converted_tier_tag = socket_helper.GenerateTierTag(socket_string, item_slot)
        AssertEqual(converted_tier_tag, tier_tag)
        decoded_socket_string, decoded_item_slot = socket_helper.DecodeTierTag(tier_tag)
        AssertEqual(decoded_socket_string, normalized_socket_string)
        AssertEqual(decoded_item_slot, string_helper.ToTitleCase(item_slot))
    print('TestGenerateDecodeTierTag passed!')

def TestGenerateSocketConditions():
    for socket_string, item_slot, _, _, expected_condition_lines in kSocketStringTestCases:
        condition_lines = socket_helper.GenerateSocketConditions(socket_string, item_slot)
        AssertEqual(condition_lines, expected_condition_lines)
    print('TestGenerateSocketConditions passed!')

def TestGenerateSocketConditionsInvalidInput():
    for socket_string in kInvalidSocketStrings:
        try:
            conditions_list = socket_helper.GenerateSocketConditions(socket_string, item_slot='any')
        except RuntimeError:
            # This should happen
            pass
        else:
            print('Unexpected sucessful parse of "{}"'.format(socket_string))
            print('Result conditions_list: {}'.format(conditions_list))
            AssertFailure()
    print('TestGenerateSocketConditionsInvalidInput passed!')

def main():
    TestNormalizeSocketString()
    TestGenerateDecodeTierTag()
    TestGenerateSocketConditions()
    TestGenerateSocketConditionsInvalidInput()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()