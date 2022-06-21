from typing import List, Tuple

import parse_helper
import simple_parser
from type_checker import CheckType

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
        'Split', 'Veiled Prefix', 'Veiled Suffix'}

kInfluenceProperties = {'Shaper Item', 'Elder Item', 'Crusader Item', 'Warlord Item',
                        'Redeemer Item', 'Hunter Item', 'Searing Exarch Item', 'Eater of Worlds Item'}

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
            self.properties_map['Replica Unique'] = True
            # Consideration: do we want to remove 'Replica ' from the Name?
        # 5. Apply convenience adjustments
        # Parse first int value from 'Quality', 'Stack Size', 'Experience', 'Level', and Requirements
        for keyword in ['Quality', 'Stack Size', 'Experience', 'Level',
                'Required Level', 'Required Str', 'Required Dex', 'Required Int']:
            if (keyword in self.properties_map):
                first_int = simple_parser.ParseInts(self.properties_map[keyword])[0]
                self.properties_map[keyword] = first_int
        # Convert 'Unidentified' to 'Identified'
        self.properties_map['Identified'] = not self.properties_map['Unidentified']
        # 6. Final fixes
        # If item is Superior and Unidentified, BaseType currently looks like:
        # 'Superior Maze of the Minotaur Map'
        if (not self.properties_map['Identified'] and (self.properties_map.get('Quality', 0) > 0)
                and self.properties_map['BaseType'].startswith('Superior ')):
            self.properties_map['BaseType'] = self.properties_map['BaseType'][len('Superior '):]
    # End ParseItemText
    
    def __repr__(self):
        raw_text = '\n'.join(self.text_lines)
        properties_map_text = '\n'.join(str((k, v)) for k, v in self.properties_map.items())
        return 'Raw Item Text:\n' + raw_text + '\n\nProperties Map:\n' + properties_map_text + '\n'
    # End __repr__
    
# End class Item
