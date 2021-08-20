from typing import List, Tuple

import simple_parser
from type_checker import CheckType

kConditionsKeywordToTemplateMap = {
    'ItemLevel' : 'ItemLevel {} {}',
    'Quality' : 'Quality {} {}',
    'Rarity' : ['Rarity {}', 'Rarity {} {}'],  # operator is optional
    'Class' : 'Class {}',
    'BaseType' : 'BaseType {}',
    'LinkedSockets' : 'LinkedSockets {}',
    'Corrupted': 'Corrupted {}'}

kOperators = {'=', '==', '!', '<', '<=', '>', '>='}

# A generic rule line is of the form:
# <keyword> <optional: operator> <values>
def ParseRuleLineGeneric(line: str) -> Tuple[str, str, List[str]]:
    CheckType(line, 'line', str)
    # Cleanup whitespace and comment character if exists
    line = line.strip()
    if (line.startswith('#')):
        line = line[1:].strip()
    # Split into keyword, optional_operator, values
    space_split_list: List[str] = line.split(' ')
    keyword: str = space_split_list[0]
    operator: str = ''
    values_string: str = ''
    if (space_split_list[1] in kOperators):
        operator = space_split_list[1]
        values_string = ' '.join(space_split_list[2:])
    else:
        values_string = ' '.join(space_split_list[1:])
    values_list = []
    # Now we want to parse the values string into a list of items
    # Items in values string can be either space-separated, or enclosed in quotes
    # We will assume a single convention is used for all items in the same rule
    if ('"' in values_string):  # assume all values are enclosed in quotes
        values_list = simple_parser.ParseEnclosedBy(values_string, '"')
    else:
        values_list = values_string.split(' ')
    return keyword, operator, values_list

def Test():
    test_list = [
        'BaseType "Sorcerer Boots" "Sorcerer Gloves" "Crystal Belt" "Hubris Circlet"',
        'ItemLevel >= 84',
        'Corrupted False',
        'Rarity < Rare',
        '	Class "Map Fragments"',
        '# 	 Class == "Rune Daggers" "Sceptres" "Wands"',
        'Class "Boots"']
    for line in test_list:
        keyword, operator, values_list = ParseRuleLineGeneric(line)
        print('keyword = "{}", operator = "{}", values_list = {}'.format(
                keyword, operator, values_list))

Test()

