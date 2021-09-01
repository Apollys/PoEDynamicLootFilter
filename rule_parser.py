import operator
from typing import List, Tuple

import multiset
import simple_parser
from type_checker import CheckType, CheckType2

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

# Checks substring containment if operands are strings, otherwise equality
def UnspecifiedOperator(item_property, rule_value) -> bool:
    if (isinstance(item_property, str) and isinstance(rule_value, str)):
        return rule_value in item_property
    return rule_value == item_property
# End UnspecifiedOperator

kOperatorsMap = {'=' : operator.contains,
                 '==' : operator.eq,
                 '' : UnspecifiedOperator,
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

# Implemented keywords for items
kBinaryProperties = ['Unidentified', 'Corrupted', 'Mirrorred', 'Alternate Quality']

kInfluenceProperties = ['Shaper Item', 'Elder Item', 'Crusader Item', 'Warlord Item',
                        'Redeemer Item', 'Hunter Item']

kOtherImportantProperties = ['Item Level', 'Stack Size', 'Map Tier', 'Quality']

# Keywords in items have spaces, in loot filter ruels they don't
# This function allows us to translate between the two.
# Note: it modifies the input dict and does not return anything.
def RemoveSpacesFromKeys(d: dict):
    original_keys: list = list(d.keys())
    for key in original_keys:
        if (' 'in key):
            new_key = key.replace(' ', '')
            d[new_key] = d[key]
            d.pop(key)
# End RemoveSpacesFromKeys

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
                    # Parse int value from quality string: '+20% (augmented)' -> 20
                    if (property_name == 'Quality'):
                        quality_string = item_properties[property_name]
                        [item_properties[property_name]] = simple_parser.ParseInts(
                            quality_string)
                    elif (property_name == 'StackSize'):
                        _, parse_result = simple_parser.ParseFromTemplate(
                                item_properties[property_name], '{}/{}')
                        item_properties[property_name] = [int(s) for s in parse_result]
                    # Handle all single integer properties
                    else:
                        item_properties[property_name] = int(item_properties[property_name])
                # Handle Sockets separately:
                #  - Parse sockets as item_properties['Sockets'] = {'R', 'B', 'G', 'A'}
                #  - Parse links as item_properties['SocketGroups'] = [{'R', 'G', 'B'}, {A}]
                #  - Each set above is a Multiset object (defined in multiset.py)
                elif (property_name == 'Sockets'):
                    socket_groups = [multiset.Multiset(group.split('-'))
                            for group in value_string.split(' ')]
                    sockets = multiset.Multiset(
                            socket for group in socket_groups for socket in group)
                    item_properties['Sockets'] = sockets
                    item_properties['SocketGroups'] = socket_groups
                    item_properties['NumSockets'] = len(sockets)
                    item_properties['NumLinkedSockets'] = max(len(group) for group in socket_groups)
    # Identified is handled backwards in item text and loot filter rules
    item_properties['Identified'] = not item_properties['Unidentified']
    # Handle alternate quality gems (item will have line "Alternate Quality")
    if ((item_properties['Rarity'] == 'Gem') and item_properties['Alternate Quality']):
        print(item_properties['BaseType'])
        _, [quality_type, gem_name] = simple_parser.ParseFromTemplate(
                item_properties['BaseType'], '{} {}')
        item_properties['GemQualityType'] = quality_type
        item_properties['BaseType'] = gem_name
    # Todo: handle requirements section separately
    # Remove all spaces from keys in item properties to match loot filter syntax
    RemoveSpacesFromKeys(item_properties)
    return item_properties
# End ParseItem

# Implemented/ignore keywords for Rules
kImplementedBinaryKeywords = ['Identified', 'Corrupted', 'Mirrorred', 'AlternateQuality']
kImplementedOtherKeywords = ['Class', 'Rarity', 'BaseType', 'ItemLevel', 'MapTier', 'Quality',
                             'HasInfluence', 'GemQualityType']
# Ignore any rules with any of the following conditions:
kIgnoreKeywords = ['AreaLevel', 'AnyEnchantment', 'FracturedItem', 'SynthesisedItem',
                   'BlightedMap', 'HasExplicitMod', 'SocketGroup', 'GemLevel']

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
    # Ignore any rules with keywords defined in kIgnoreKeywords
    if (keyword in kIgnoreKeywords):
        return False
    elif (keyword in kImplementedBinaryKeywords):
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
                if (simple_parser.IsInt(rule_value)):
                    rule_value = int(rule_value)
                match = any(kOperatorsMap[operator](item_property, rule_value)
                            for item_property in item_properties_list)
    # Handle socket conditions separately
    # For now we only check the number of sockets and linked sockets, not colors
    elif (keyword == 'Sockets'):
        if ('Sockets' not in item_properties):
            return False
        int_list = simple_parser.ParseInts(values_list[0])
        if (len(int_list) == 1):
            [required_num_sockets] = int_list
            op_func = kOperatorsMap[operator]
            match = op_func(item_properties['NumSockets'], required_num_sockets)
    elif (keyword == 'LinkedSockets'):
        if ('Sockets' not in item_properties):
            return False
        int_list = simple_parser.ParseInts(values_list[0])
        if (len(int_list) == 1):
            [required_num_linked_sockets] = int_list
            match = item_properties['NumLinkedSockets'] == required_num_linked_sockets
    # Todo: handle rest of cases
    return match
# End CheckRuleConditionMatchesItem

def CheckRuleMatchesItem(parsed_rule_lines: List[tuple], item_properties: dict) -> bool:
    CheckType2(parsed_rule_lines, 'parsed_rule_lines', list, tuple)
    CheckType(item_properties, 'item_properties', dict)
    for parsed_rule_line in parsed_rule_lines:
        match = CheckRuleConditionMatchesItem(parsed_rule_line, item_properties)
        if (not match): 
            return False
    return True
# End CheckRuleMatchesItem

def CheckRuleMatchesItemText(parsed_rule_lines: List[str], item_lines: List[str]) -> bool:
    CheckType2(parsed_rule_lines, 'parsed_rule_lines', list, tuple)
    CheckType2(item_lines, 'item_lines', list, str)
    item_properties: dict = ParseItem(item_lines)
    return CheckRuleMatchesItem(parsed_rule_lines, item_properties)
# End CheckRuleMatchesItemText
                

test_item = \
'''Item Class: Active Skill Gems
Rarity: Gem
Divergent Vitality
--------
Aura, Spell, AoE
Level: 16
Reservation: 189 Mana
Cooldown Time: 1.20 sec
Cast Time: Instant
Quality: +13% (augmented)
Alternate Quality
--------
Requirements:
Level: 60
Str: 103
--------
Casts an aura that grants life regeneration to you and your allies.
--------
+15 to radius
You and nearby Allies Regenerate 135 Life per second
You and nearby Allies deal 2% increased Damage while on Full Life
--------
Experience: 7879780/16039890
--------
Place into an item socket of the right colour to gain this skill...'''

test_rule = \
'''Show # $type->gems-exceptional $tier->divt1
GemQualityType Divergent
Class "Gems"
BaseType "Anger" "Vitality"
SetFontSize 45
SetTextColor 0 0 125 255
SetBorderColor 0 0 125 255
SetBackgroundColor 255 255 255 255
PlayEffect Red
MinimapIcon 0 Red Star
PlayAlertSound 1 300
'''

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
    
    match_flag = CheckRuleMatchesItemText(parsed_rule_lines, item_lines)
    print('match_flag = {}'.format(match_flag))

#Test()

