import operator
from typing import List, Tuple

import multiset
import parse_helper
import simple_parser
from type_checker import CheckType

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

kRarityToIntMap = {'Normal' : 0, 'Magic' : 1, 'Rare' : 2, 'Unique' : 3}

kArithmeticComparisonsOpMap = {'<'  : operator.lt,
                               '<=' : operator.le,
                               '>'  : operator.gt,
                               '>=' : operator.ge}

# Generates an arithemtic comparison function that takes two parameters and returns a bool
# Parameters are expected to be strings, but can represent either ints or rarity values
def ArithmeticComparisonFunc(op_string: str):
    CheckType(op_string, 'op_string', str)
    def ArithmeticCompare(left: str, right: str) -> bool:
        CheckType(left, 'left', str)
        CheckType(right, 'right', str)
        if (simple_parser.IsInt(left) and simple_parser.IsInt(right)):
            return kArithmeticComparisonsOpMap[op_string](int(left), int(right))
        elif ((left in kRarityToIntMap) and (right in kRarityToIntMap)):
            return kArithmeticComparisonsOpMap[op_string](
                    kRarityToIntMap[left], kRarityToIntMap[right])
        return False
    # End ArithmeticCompare
    return ArithmeticCompare
# End ArithmeticCompare

kOperatorsMap = { **{'=' : operator.contains,
                     '' : operator.contains,
                     '==' : operator.eq,
                     '!' : operator.ne},
                  **{op_string : ArithmeticComparisonFunc(op_string)
                        for op_string in kArithmeticComparisonsOpMap} }


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
    values_list = parse_helper.ConvertValuesStringToList(values_string)
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
kBinaryProperties = ['Unidentified', 'Corrupted', 'Mirrorred', 'Alternate Quality', 'Replica']

kInfluenceProperties = ['Shaper Item', 'Elder Item', 'Crusader Item', 'Warlord Item',
                        'Redeemer Item', 'Hunter Item']

kOtherImportantProperties = ['Item Level', 'Stack Size', 'Map Tier', 'Quality', 'Gem Level']

# Keywords in items have spaces, in loot filter rules they don't
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

# Parses an item's text description into a dictionary of {'property_name' : 'property_value'}
# Property values will always be strings - we convert to int later for arithmetic comparisons
# Exception: 'Sockets' and 'LinkedSockets' are multisets, so socket colors can be checked
def ParseItem(item_lines: List[str]) -> dict:
    CheckType(item_lines, 'item_lines', list)
    # Initialize binary properties to False by default
    item_properties = {binary_property : False for binary_property in kBinaryProperties}
    item_properties['HasInfluence'] = []  # no influence by default
    item_lines = [line.strip() for line in item_lines]
    # Parse first section: Class, Rarity, and Name, BaseType
    # Class
    _, [class_value_string] = simple_parser.ParseFromTemplate(item_lines[0], 'Item Class: {}')
    if (class_value_string == 'Stackable Currency'): class_value_string = 'Currency'
    item_properties['Class'] = class_value_string
    # Rarity
    _, [rarity_value_string] = simple_parser.ParseFromTemplate(item_lines[1], 'Rarity: {}')
    item_properties['Rarity'] = rarity_value_string
    # Name and BaseType
    has_name: bool = not item_lines[3].startswith('-')
    item_properties['Name'] = item_lines[2] if has_name else ''
    base_type_line_index = 3 if has_name else 2
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
                        [quality_int] = simple_parser.ParseInts(quality_string)
                        item_properties[property_name] = str(quality_int)
                    elif (property_name == 'StackSize'):
                        # Eliminate commas in stack size numbers
                        item_properties[property_name] = item_properties[property_name].replace(
                                ',', '')
                        _, parse_result = simple_parser.ParseFromTemplate(
                                item_properties[property_name], '{}/{~}')
                        item_properties[property_name] = parse_result[0]
                    # Handle all single integer properties
                    else:
                        item_properties[property_name] = item_properties[property_name]
                # Handle Gem Level (just shows up as "Level", always above Requirements Level)
                if ((property_name == 'Level') and (item_properties['Rarity'] == 'Gem')
                        and ('GemLevel' not in item_properties)):
                    item_properties['GemLevel'] = value_string
                # Handle Sockets separately:
                #  - Example: 'R-B-B A'
                #  - Parse sockets as item_properties['Sockets'] = {'R', 'B', 'B', 'A'}
                #  - Parse links as item_properties['SocketGroups'] = [{'R', 'B', 'B'}, {A}]
                #  - Each set above is a Multiset object (defined in multiset.py)
                elif (property_name == 'Sockets'):
                    socket_groups = [multiset.Multiset(group.split('-'))
                            for group in value_string.split(' ')]
                    sockets = multiset.Multiset(
                            socket for group in socket_groups for socket in group)
                    item_properties['Sockets'] = sockets
                    item_properties['SocketGroups'] = socket_groups
                    item_properties['NumSockets'] = str(len(sockets))
                    item_properties['NumLinkedSockets'] = str(
                            max(len(group) for group in socket_groups))
    # Identified is handled backwards in item text and loot filter rules
    item_properties['Identified'] = not item_properties['Unidentified']
    # Handle alternate quality gems (item will have line "Alternate Quality")
    if ((item_properties['Rarity'] == 'Gem') and item_properties['Alternate Quality']):
        _, [quality_type, gem_name] = simple_parser.ParseFromTemplate(
                item_properties['BaseType'], '{} {}')
        item_properties['GemQualityType'] = quality_type
        item_properties['BaseType'] = gem_name
    # Check for replica uniques (item rarity is unique, first word of name is "Replica")
    item_properties['Replica'] = ((item_properties['Rarity'] == 'Unique') and
                                  (item_properties['Name'].startswith('Replica ')))
    # Todo: handle requirements section separately
    # Remove all spaces from keys in item properties to match loot filter syntax
    RemoveSpacesFromKeys(item_properties)
    return item_properties
# End ParseItem

# Implemented/ignore keywords for Rules
kImplementedBinaryKeywords = ['Identified', 'Corrupted', 'Mirrorred', 'AlternateQuality', 'Replica']
kImplementedOtherKeywords = ['Class', 'Rarity', 'BaseType', 'ItemLevel', 'MapTier', 'Quality',
                             'HasInfluence', 'GemLevel', 'GemQualityType', 'StackSize']
# Ignore any rules with any of the following conditions:
kIgnoreKeywords = ['AreaLevel', 'AnyEnchantment', 'FracturedItem', 'SynthesisedItem',
                   'BlightedMap', 'HasExplicitMod', 'SocketGroup',
                   'HasSearingExarchImplicit', 'HasEaterOfWorldsImplicit', 'UberBlightedMap',
                   'Scourged', 'ArchnemesisMod']

# We are making a few basic assumptions that the rules are written "reasonably" here:
#  - For binary properties, there will not be a "not equals" operator, i.e.
#    we will not see: "Corrupted ! False"
#    (This is equivalent to "Corrupted True")
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
        # Check for any of the item properties to match any of the rule properties
        # For example, if an item HasInfluence: Hunter, Redeemer,
        # and the rule line is HasInfluence: Crusader, Redeemer, 
        # then the item matches, because it matches any of the keywords in the rule line
        else:
            item_properties_list = (item_properties[keyword] if
                    isinstance(item_properties[keyword], list) else [item_properties[keyword]])
            match = any(kOperatorsMap[operator](item_property, rule_value)
                        for item_property in item_properties_list
                        for rule_value in values_list)
    # Handle socket conditions separately
    # For now we only check the number of sockets and linked sockets, not colors
    elif (keyword == 'Sockets'):
        if ('Sockets' not in item_properties):
            return False
        int_list = simple_parser.ParseInts(values_list[0])
        if (len(int_list) == 1):
            [required_num_sockets] = int_list
            op_func = kOperatorsMap[operator]
            match = op_func(item_properties['NumSockets'], str(required_num_sockets))
    elif (keyword == 'LinkedSockets'):
        if ('Sockets' not in item_properties):
            return False
        int_list = simple_parser.ParseInts(values_list[0])
        if (len(int_list) == 1):
            [required_num_linked_sockets] = int_list
            match = item_properties['NumLinkedSockets'] == str(required_num_linked_sockets)
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
Vitality
--------
Aura, Spell, AoE
Level: 1
Reservation: 28 Mana
Cooldown Time: 1.20 sec
Cast Time: Instant
Quality: +10% (augmented)
--------
Requirements:
Level: 10
Str: 22
--------
Casts an aura that grants life regeneration to you and your allies.
--------
20% increased Area of Effect
You and nearby Allies Regenerate 10 Life per second
--------
Experience: 1/9569
--------
Place into an item socket of the right colour to gain this skill. Right click to remove from a socket.'''

test_rule = \
'''Show # $type->gems-generic $tier->lt1
GemLevel >= 21
Class "Gems"
SetFontSize 45
SetTextColor 20 240 240 255
SetBorderColor 240 0 0 255
SetBackgroundColor 70 0 20 255
PlayAlertSound 1 300
PlayEffect Red
MinimapIcon 0 Red Triangle
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

