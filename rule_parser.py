import operator
from typing import List, Tuple

import simple_parser
from type_checker import CheckType

# =================================== Generic Helper ===================================

# Parses values string into a list of items
# Items in values string can be either space-separated, or enclosed in quotes
# Assumes a single convention is used for all items in the same rule
def ParseValuesString(values_string: str) -> List[str]:
    CheckType(values_string, 'values_string', str)
    if ('"' in values_string):  # assume all values are enclosed in quotes
        values_list = simple_parser.ParseEnclosedBy(values_string, '"')
    else:
        values_list = values_string.split(' ')
    return values_list
# End ParseValuesString   

# ==================================== Rule Parsing ====================================

# Note: not using this currently
kConditionsKeywordToTemplateMap = {
    'ItemLevel' : 'ItemLevel {} {}',
    'Quality' : 'Quality {} {}',
    'Rarity' : ['Rarity {}', 'Rarity {} {}'],  # operator is optional
    'Class' : 'Class {}',
    'BaseType' : 'BaseType {}',
    'LinkedSockets' : 'LinkedSockets {}',
    'Corrupted': 'Corrupted {}'}

kOperatorsMap = {'=' : operator.contains,
                 '==' : operator.eq,
                 '' : operator.eq,  # absence of any operator implies equals
                 '!' : operator.ne,
                 '<' : operator.lt,
                 '<=' : operator.le,
                 '>' : operator.gt,
                 '>=' : operator.ge}
                 

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
    if (len(space_split_list) > 1):
        if (space_split_list[1] in kOperatorsMap):
            operator = space_split_list[1]
            values_string = ' '.join(space_split_list[2:])
        else:
            values_string = ' '.join(space_split_list[1:])
    values_list = ParseValuesString(values_string)
    return keyword, operator, values_list

# ==================================== Item Parsing ====================================

# The first 3-4 lines of an item will always be: Item Class, Rarity, (optional name), BaseType,
# which will then be followed by a line of 8 dashes ('-'), for example:
'''
Item Class: Map Fragments
Rarity: Normal
Rusted Breach Scarab
--------
'''
# or
'''
Item Class: Gloves
Rarity: Rare
Mind Grip
Conjurer Gloves
'''

# After that, each line can be parsed on its own except Requirements, which come as a section:
'''
--------
Requirements:
Level: 70
Dex: 155
Int: 159
--------
'''

kImportantProperties = ['Sockets', 'Item Level', 'Stack Size', 'Map Tier', 'Quality', 
                        'Shaper Item', 'Elder Item', 'Crusader Item', 'Warlord Item',
                        'Redeemer Item', 'Hunter Item', 'Unidentified', 'Corrupted']

# Parses an item's text description into a dictionary of {'property_name' : property_value}
# Property value is either a single string, or a list of strings if there are multiple values
def ParseItem(item_lines: List[str]) -> dict:
    CheckType(item_lines, 'item_lines', list)
    item_properties = {}
    item_lines = [line.strip() for line in item_lines]
    # Parse first section: Class, Rarity, and BaseType
    # Class
    _, [class_value_string] = simple_parser.ParseFromTemplate(item_lines[0], 'Item Class: {}')
    if (class_value_string == 'Stackable Currency'): class_value_string = 'Currency'
    item_properties['Class'] = class_value_string
    # Rarity
    _, [rarity_value_string] = simple_parser.ParseFromTemplate(item_lines[1], 'Rarity: {}')
    item_properties['Rarity'] = rarity_value_string
    # BaseType
    base_type_line_index = 2 if (item_lines[3].startswith('-')) else 3
    item_properties['BaseType'] = item_lines[base_type_line_index]
    # Parse the rest line-by-line, saving important properties (ignoring requirements for now)
    for line in item_lines[base_type_line_index + 2 :]:
        parse_success, token_list = simple_parser.ParseFromTemplate(line, '{}: {}')
        if (parse_success):
            property_name, value_string = token_list
            if (property_name in kImportantProperties):
                # Remove spaces to match loot filter syntax
                property_name = property_name.replace(' ', '')
                item_properties[property_name] = value_string
                # Do any additional parsing here
                # "Fix" quality string: from '+20% (augmented)' to '20'
                if (property_name == 'Quality'):
                    _, [quality_string] = simple_parser.ParseFromTemplate(
                            item_properties[property_name], '+{}%{~}')
                    item_properties[property_name] = quality_string
        # Check for binary state properties (no value, just represented by presence/absence)
        elif (line in kImportantProperties):
            item_properties[line] = True
    # Todo: handle requirements section separately
    return item_properties
# End ParseItem

def CheckRuleConditionMatchesItem(parsed_rule_line: tuple, item_properties: dict) -> bool:
    keyword, operator, values_list = parsed_rule_line
    match = True
    if (keyword in ['Class', 'Rarity', 'BaseType', 'ItemLevel', 'MapTier']):
        if (keyword not in item_properties):
            match = False
        # Check for direct match of any value, if there are multiple values
        elif (len(values_list) > 1):
            match = item_properties[keyword] in values_list
        # Check for operator match when there is only one value
        else:  # len(values_list) == 1
            [rule_value] = values_list
            match = kOperatorsMap[operator](item_properties[keyword], rule_value)
        if (not match): return False
    # Todo: handle rest of cases
    return match
# End CheckRuleConditionMatchesItem

def CheckRuleMatchesItem(parsed_rule_lines: List[str], item_lines: List[str]) -> bool:
    CheckType(parsed_rule_lines, 'parsed_rule_lines', list)
    CheckType(item_lines, 'item_lines', list)
    item_properties: dict = ParseItem(item_lines)
    for parsed_rule_line in parsed_rule_lines[1:]:
        match = CheckRuleConditionMatchesItem(parsed_rule_line, item_properties)
        if (not match): 
            return False
    return True
# End CheckRuleMatchesItem
                



def Test():
    item_lines = test_item.split('\n')
    rule_lines = test_rule.split('\n')
    parsed_rule_lines = [ParseRuleLineGeneric(rule_line) for rule_line in rule_lines]
    print('parsed_rule_lines = ')
    for line in parsed_rule_lines: print (line)
    print()
    match_flag = CheckRuleMatchesItem(parsed_rule_lines, item_lines)
    print('match_flag = {}'.format(match_flag))

