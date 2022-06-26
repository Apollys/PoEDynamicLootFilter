'''
This file defines the class Item.

It also defines the free function:
 - RuleMatchesItem(rule: LootFilterRule, item: Item) -> bool
'''

from typing import List, Tuple

import consts
from loot_filter_rule import LootFilterRule
from multiset import Multiset
import parse_helper
import simple_parser
from type_checker import CheckType, CheckTypesMatch

# Sample Item text, copied with Ctrl-C:
'''
Item Class: Helmets
Rarity: Rare
Bramble Dome
Magistrate Crown
--------
Quality: +20% (augmented)
Armour: 192 (augmented)
Energy Shield: 66 (augmented)
--------
Requirements:
Level: 70
Str: 64
Dex: 98
Int: 68
--------
Sockets: G-G-G-B 
--------
Item Level: 80
--------
Barrage fires an additional Projectile (enchant)
--------
15% increased Global Accuracy Rating
+22 to maximum Energy Shield
+32 to maximum Life
+60 to maximum Mana
+42% to Cold Resistance
10% increased Light Radius
Nearby Enemies have -9% to Cold Resistance
+69 to maximum Life (crafted)
'''

kBlockDivider = '--------'

kBinaryProperties = {'Alternate Quality', 'Unidentified', 'Mirrored', 'Corrupted', 'Synthesised Item', 'Fractured Item',
        'Split', 'Veiled Prefix', 'Veiled Suffix', 'Searing Exarch Item', 'Eater of Worlds Item', 'Shaped Map'}

kInfluenceProperties = {'Shaper Item', 'Elder Item', 'Crusader Item', 'Warlord Item',
                        'Redeemer Item', 'Hunter Item'}

kAllBinaryProperties = kBinaryProperties | kInfluenceProperties  # set union

class Item:
    '''
    Member variables:
      - self.text_lines: List[str]
      - self.properties_map: dict mapping keyword -> value
    '''
    def __init__(self, text_lines: List[str] or str):
        if (isinstance(text_lines, str)):
            text_lines = text_lines.split('\n')
        CheckType(text_lines, 'text_lines', list, str)
        self.text_lines = [line.strip() for line in text_lines]
        self.properties_map = {}
        self.ParseItemText()
    # End __init__
    
    # Helper function for ParseItemText
    def PrependTextLine(self, index: int, prefix: str):
        CheckType(index, 'index', int)
        CheckType(prefix, 'prefix', str)
        self.text_lines[index] = prefix + self.text_lines[index]
    # End PrependTextLine
    
    # Overwrite self.text_lines so they can be parsed as {keyword}: {value}
    # into the properties_map, then apply certain adjustments for convenience.
    # TODO: A list of BaseTypes is required to parse the BaseType from Magic items.
    # TODO: Parsing alt-copied text is not yet supported.
    def ParseItemText(self):
        # 1. Handle header block
        header_end_index = self.text_lines.index(kBlockDivider) - 1
        self.PrependTextLine(header_end_index, 'BaseType: ')
        if (header_end_index == 3):
            self.PrependTextLine(header_end_index - 1, 'Name: ')
        # 2. Handle requirements block, if it exists
        requirements_start_index = parse_helper.FindElement('Requirements:', self.text_lines)
        if (requirements_start_index != None):
            i = requirements_start_index + 1
            while (self.text_lines[i] != kBlockDivider):
                self.PrependTextLine(i, 'Required ')
                i += 1
        # 3. Traverse self.text_lines and parse as {keyword}: {value} where possible
        for line in self.text_lines:
            parse_success, parse_result = simple_parser.ParseFromTemplate(line, '{}: {}')
            if (parse_success):
                keyword, value_string = parse_result
                self.properties_map[keyword] = (int(value_string)
                        if simple_parser.IsInt(value_string) else value_string)
        # 4. Parse binary properties
        for binary_property in kAllBinaryProperties:
            self.properties_map[binary_property] = False
        for line in self.text_lines:
            if (line in kAllBinaryProperties):
                self.properties_map[line] = True
        # Check for Replica Unique
        if ((self.properties_map['Rarity'] == 'Unique') and
                self.properties_map.get('Name', '').startswith('Replica ')):
            self.properties_map['Replica'] = True
            # Consideration: do we want to remove 'Replica ' from the Name?
        # Get Alternate Quality Type
        if ((self.properties_map['Rarity'] == 'Gem') and self.properties_map['Alternate Quality']):
            _, [quality_type, gem_name] = simple_parser.ParseFromTemplate(
                    self.properties_map['BaseType'], '{} {}')
            self.properties_map['Gem Quality Type'] = quality_type
            self.properties_map['BaseType'] = gem_name
        # 5. Apply convenience adjustments
        # Parse first int value from 'Quality', 'Stack Size', 'Experience', 'Level', and Requirements
        for keyword in ['Quality', 'Stack Size', 'Experience', 'Level',
                'Required Level', 'Required Str', 'Required Dex', 'Required Int']:
            if (keyword in self.properties_map):
                first_int = simple_parser.ParseInts(self.properties_map[keyword])[0]
                self.properties_map[keyword] = first_int
        # 6. Miscellaneous fixes
        # If item is Superior and Unidentified, BaseType currently looks like:
        # 'Superior Maze of the Minotaur Map'
        if (self.properties_map['Unidentified'] and (self.properties_map.get('Quality', 0) > 0)
                and self.properties_map['BaseType'].startswith('Superior ')):
            self.properties_map['BaseType'] = self.properties_map['BaseType'][len('Superior '):]
        # If an item doesn't have Quality, give it Quality = 0
        if ('Quality' not in self.properties_map):
            self.properties_map['Quality'] = 0
        # 7. Finally, convert properties to the format used by loot filter rules
        self.ConvertPropertiesToRuleFormat()
    # End ParseItemText
    
    def ConvertPropertiesToRuleFormat(self):
        # Convert 'Unidentified' to 'Identified'
        self.properties_map['Identified'] = not self.properties_map['Unidentified']
        # Convert 'Item Class' to 'Class'
        if ('Item Class' in self.properties_map):
            self.properties_map['Class'] = self.properties_map['Item Class']
            self.properties_map.pop('Item Class')
        # Convert 'Searing Exarch Item' -> 'HasSearingExarchImplicit',
        # and 'Eater of Worlds Item' -> 'HasEaterOfWorldsImplicit'.
        self.properties_map['HasSearingExarchImplicit'] = self.properties_map['Searing Exarch Item']
        self.properties_map['HasEaterOfWorldsImplicit'] = self.properties_map['Eater of Worlds Item']
        # Create a list of Influence keywords saved with key 'HasInfluence'
        # Conversion: 'Shaper Item' -> 'Shaper' (remove trailing ' Item')
        # Note: for testing convenience, we use a sorted list (rather than a set)
        self.properties_map['HasInfluence'] = []
        for item_influence_keyword in kInfluenceProperties:
            if (self.properties_map[item_influence_keyword]):
                self.properties_map['HasInfluence'].append(item_influence_keyword[:-len(' Item')])
        self.properties_map['HasInfluence'].sort()
        # Shaper and Elder Guardian maps match rules of the form 'HasInfluence Shaper/Elder', but
        # they don't have 'Shaper/Elder Item' lines.  Instead, they are marked with an implicit:
        # 'Area is influenced by The Shaper/Elder (implicit)'
        if (self.properties_map.get('Class', '') == 'Maps'):
            influenced_by_template = 'Area is influenced by The {}'
            if (parse_helper.IsSubstringInLines(influenced_by_template.format('Shaper'), self.text_lines)):
                self.properties_map['HasInfluence'].append('Shaper')
            if (parse_helper.IsSubstringInLines(influenced_by_template.format('Elder'), self.text_lines)):
                self.properties_map['HasInfluence'].append('Elder')
        if (self.properties_map['HasInfluence'] == []):
            self.properties_map['HasInfluence'] = ['None']
        # Remove spaces from keys
        # Copy dictionary items to avoid 'RuntimeError: dictionary changed size during iteration'
        for keyword, value in list(self.properties_map.items()):
                if (' ' in keyword):
                    self.properties_map.pop(keyword)
                    self.properties_map[keyword.replace(' ', '')] = value
        # Convert Level to GemLevel (if Rarity is Gem)
        if (self.properties_map.get('Rarity', '') == 'Gem'):
            self.properties_map['GemLevel'] = self.properties_map['Level']
            self.properties_map.pop('Level')
        # Sockets, SocketGroups, NumSockets, and LinkedSockets
        # Example:  'R-B-B A'
        #  -> Sockets = Multiset(R, B, B, A)
        #  -> SocketGroups = [Muiltiset(R, B, B), Multiset(A)]
        #  -> NumSockets = 4
        #  -> LinkedSockets = 3
        if ('Sockets' in self.properties_map):
            sockets_string = self.properties_map['Sockets']
            self.properties_map['Sockets'] = Multiset(sockets_string.replace('-', ' ').split(' '))
            self.properties_map['SocketGroups'] = [Multiset(group_string.split('-'))
                    for group_string in sockets_string.split(' ')]
            self.properties_map['NumSockets'] = len(self.properties_map['Sockets'])
            self.properties_map['LinkedSockets'] = max(
                    len(socket_group) for socket_group in self.properties_map['SocketGroups'])
        # Sentinels: Item has class 'Sentinel', filter uses class 'Sentinel Drone'
        if (self.properties_map['Class'] == 'Sentinel'):
            self.properties_map['Class'] = 'Sentinel Drone'
    # End ConvertPropertiesToRuleFormat
    
    def __repr__(self):
        raw_text = '\n'.join(self.text_lines)
        properties_map_text = '\n'.join(str((k, v)) for k, v in self.properties_map.items())
        return 'Raw Item Text:\n' + raw_text + '\n\nProperties Map:\n' + properties_map_text + '\n'
    # End __repr__
    
# End class Item

# ==================================== Rule-Item Matching ====================================

'''
Conversion from item properties to rule properties
 - Influence: Item property looks like ('Shaper Item', 'True'),
    LootFilterRule property looks like ('HasInfluence', '', ['Shaper', ...])
 - Gem Level: Item property is 'Level', Rule property is 'GemLevel'

'''

kRarityToIntMap = {'Normal' : 0, 'Magic' : 1, 'Rare' : 2, 'Unique' : 3}

# If empty operator, we check if rule value is a substring of item value. For example:
#  - Item: Class 'Stackable Currency'
#  - Rule: Class 'Currency'
# This should match.
def EmptyOpFunc(item_value, rule_value):
    CheckTypesMatch(item_value, 'item_value', rule_value, 'rule_value')
    # If not string, just use equality
    if (not isinstance(item_value, str)):
        return item_value == rule_value
    # Otherwise, use substring
    return rule_value in item_value
# EmptyOpFunc

def OperatorFunc(op_string: str, item_value, rule_value) -> bool:
    item_value = simple_parser.ParseValueDynamic(item_value)
    rule_value = simple_parser.ParseValueDynamic(rule_value)
    CheckTypesMatch(item_value, 'item_value', rule_value, 'rule_value')
    # Convert from Rarity string to int if possible
    if ((item_value in kRarityToIntMap) and (rule_value in kRarityToIntMap)):
        item_value = kRarityToIntMap[item_value]
        rule_value = kRarityToIntMap[rule_value]
    if (op_string in consts.kOperatorMap):
        return consts.kOperatorMap[op_string](item_value, rule_value)
    elif (op_string == ''):
        return EmptyOpFunc(item_value, rule_value)
    raise RuntimeError('Unrecognized operator encountered: {}'.format(op_string))
# End OperatorFunc

def RuleMatchesItem(rule: LootFilterRule, item: Item) -> bool:
    CheckType(rule, 'rule', LootFilterRule)
    CheckType(item, 'item', Item)
    ignore_rule_flag, rule_conditions_list = rule.GetConditions()
    if (ignore_rule_flag):
        return False
    # Check if each line of the rule matches the corresponding properties of the item
    # If any rule line does not match, return False. If all match, return True.
    for keyword, op_string, values_list in rule_conditions_list:
        # If we encounter an unexpected or missing keyword, never match
        if (keyword not in item.properties_map):
            return False
        # Handle sockets - for now just count number of total sockets
        # Example socket rules:
        #  - 'Sockets == 6' -> Check item has 6 sockets
        #  - 'Sockets >= 5GGG' -> Unsupported, don't match to any item
        elif (keyword == 'Sockets'):
            if ((len(values_list) == 1) and (simple_parser.IsInt(values_list[0]))):
                rule_num_sockets = int(values_list[0])
                item_num_sockets = item.properties_map['NumSockets']
                if (not OperatorFunc(op_string, item_num_sockets, rule_num_sockets)):
                    return False
                continue
            else:
                return False
        # Check if any item property matches any of the values in the rule condition
        # Example:
        #  - item: HasInfluence Crusader, Redeemer (has Crusader AND Redeemer Influence)
        #  - rule: HasInfluence Warlord, Crusader (matches items with Warlord OR Crusader Influence)
        #  - (To create AND conditions in rules, place conditions on separate lines)
        #  -> Rule matches item, because item has Crusader Influence
        item_value_list = item.properties_map[keyword]
        if (not isinstance(item_value_list, list)):
            item_value_list = [item_value_list]
        match = any(OperatorFunc(op_string, item_value, rule_value)
                    for item_value in item_value_list
                    for rule_value in values_list)
        if (not match):
            return False
    return True
# End RuleMatchesItem