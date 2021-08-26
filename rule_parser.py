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

kBinaryProperties = ['Unidentified', 'Corrupted', 'Mirrorred']

kInfluenceProperties = ['Shaper Item', 'Elder Item', 'Crusader Item', 'Warlord Item',
                        'Redeemer Item', 'Hunter Item']

kOtherImportantProperties = ['Sockets', 'Item Level', 'Stack Size', 'Map Tier', 'Quality']

# Parses an item's text description into a dictionary of {'property_name' : property_value}
def ParseItem(item_lines: List[str]) -> dict:
    CheckType(item_lines, 'item_lines', list)
    # Initialize binary properties to False by default
    item_properties = {binary_property : False for binary_property in kBinaryProperties}
    item_properties['HasInfluence'] = []  # no influence by default
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
        if (line in kBinaryProperties):
            item_properties[line] = True
        elif (line in kInfluenceProperties):
            _, [influence_name] = simple_parser.ParseFromTemplate(line, '{} Item')
            item_properties['HasInfluence'].append(influence_name)
        else:
            parse_success, token_list = simple_parser.ParseFromTemplate(line, '{}: {}')
            if (parse_success):
                property_name, value_string = token_list
                if (property_name in kOtherImportantProperties):
                    # Remove spaces to match loot filter syntax
                    property_name = property_name.replace(' ', '')
                    item_properties[property_name] = value_string
                    # Do any additional parsing here
                    # "Fix" quality string: from '+20% (augmented)' to '20'
                    if (property_name == 'Quality'):
                        _, [quality_string] = simple_parser.ParseFromTemplate(
                                item_properties[property_name], '+{}%{~}')
                        item_properties[property_name] = quality_string
    # Identified is handled backwards in item text and loot filter rules
    item_properties['Identified'] = not item_properties['Unidentified']
    # Todo: handle requirements section separately
    return item_properties
# End ParseItem

kImplementedBinaryKeywords = ['Identified', 'Corrupted', 'Mirrorred']
kImplementedOtherKeywords = ['Class', 'Rarity', 'BaseType', 'ItemLevel', 'MapTier', 
                             'HasInfluence']

# We are making a few basic assumptions that the rules are written "reasonably" here:
#  - For binary properties, there will not be a "not equals" operator, i.e.
#    we will not see: "Corrupted ! False"
#    (This is equivalent to "Corrupted True")
#  - For a rule with multiple values, the operator will be equality, i.e. we won't see:
#    "Rarity <= Magic Rare Unique"
#   (This is equivalent to "Rarirty <= Unique")
def CheckRuleConditionMatchesItem(parsed_rule_line: tuple, item_properties: dict) -> bool:
    keyword, operator, values_list = parsed_rule_line
    match = True
    if (keyword in kImplementedBinaryKeywords):
        # Assume for now the user won't use a "not equals" operator here
        bool_values_list = [(s == 'True') for s in values_list]
        match = item_properties[keyword] in bool_values_list
    elif (keyword in kImplementedOtherKeywords):
        if (keyword not in item_properties):
            match = False
        # Check for direct match of any value, if there are multiple values
        else:
            item_properties_list = (item_properties[keyword] if
                    isinstance(item_properties[keyword], list) else [item_properties[keyword]])
            if (len(values_list) > 1):
                    match = any((item_property in values_list)
                                for item_property in item_properties_list)
            # Check for operator match when there is only one value
            else:  # len(values_list) == 1
                [rule_value] = values_list
                match = any(kOperatorsMap[operator](item_property, rule_value)
                            for item_property in item_properties_list)
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
                

test_item = \
'''Item Class: Shields
Rarity: Rare
Soul Weaver
Titanium Spirit Shield
--------
Quality: +20% (augmented)
Chance to Block: 25%
Energy Shield: 157 (augmented)
--------
Requirements:
Level: 70
Dex: 155
Int: 159
--------
Sockets: G-G-B 
--------
Item Level: 84
--------
Socketed Gems have 15% reduced Reservation
+109 to maximum Life
+48% to Fire Resistance
10% increased effect of Non-Curse Auras from your Skills
+67 to maximum Energy Shield (crafted)
--------
Shaper Item
Redeemer Item'''

test_rule = \
'''Show # $type->rare->redeemer $tier->t12
HasInfluence Redeemer
ItemLevel >= 84
Rarity <= Rare
BaseType "Cerulean Ring" "Marble Amulet" "Opal Ring" "Spiraled Wand" "Steel Ring" "Titanium Spirit Shield" "Void Fangs"
SetFontSize 45
SetTextColor 50 130 165 255
SetBorderColor 50 130 165 255
SetBackgroundColor 255 255 255 255
PlayEffect Red
MinimapIcon 0 Red Cross
PlayAlertSound 1 300'''

def Test():
    item_lines = test_item.split('\n')
    item_properties = ParseItem(item_lines)
    print('Item properties:')
    for p, v in item_properties.items():
        print('{}: {}'.format(p, v))
    print()
    
    rule_lines = test_rule.split('\n')
    parsed_rule_lines = [ParseRuleLineGeneric(rule_line) for rule_line in rule_lines]
    print('Parsed rule lines:')
    for line in parsed_rule_lines: print (line)
    print()
    
    match_flag = CheckRuleMatchesItem(parsed_rule_lines, item_lines)
    print('match_flag = {}'.format(match_flag))

#Test()
