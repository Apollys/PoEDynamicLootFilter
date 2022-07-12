import string_helper
from typing import List, Tuple

import consts
import parse_helper
from type_checker import CheckType

kValidSocketColorCharacters = 'RGBWDAX'
kSeparatorCharacters = [' ', '-']

def IsSocketStringValid(socket_string: str) -> bool:
    CheckType(socket_string, 'socket_string', str)
    return NormalizedSocketString(socket_string) != None
# End IsSocketStringValid

# Converts characters to upper case, and places spaces between socket groups.
# Example: 'X-rA-xWw' -> 'X-R A-X W W'
# Returns None if the socket string is invalid.
def NormalizedSocketString(socket_string: str) -> str:
    CheckType(socket_string, 'socket_string', str)
    if ((len(socket_string) == 0) or any(
            (c in kSeparatorCharacters for c in (socket_string[0], socket_string[-1])))):
        return None
    socket_string = socket_string.upper()
    normalized_socket_string = socket_string[0]
    for c in socket_string[1:]:
        if (normalized_socket_string[-1] in kSeparatorCharacters):
            if (c in kValidSocketColorCharacters):
                normalized_socket_string += c
            else:
                return None
        elif (c in kValidSocketColorCharacters):
            normalized_socket_string += ' ' + c
        elif (c in kSeparatorCharacters):
            normalized_socket_string += c
        else:
           return None
    return normalized_socket_string
# End NormalizedSocketString

# Generates a tier tag from the given socket string, which is formed
# by the concatenation of:
#  - Lower case normalized socket string with underscores replacing spaces
#  - Two underscores
#  - Lower case item slot string with underscores replacing spaces
def GenerateTierTag(socket_string: str, item_slot: str) -> str:
    CheckType(socket_string, 'socket_string', str)
    CheckType(item_slot, 'item_slot', str)
    return (NormalizedSocketString(socket_string).lower().replace(' ', '_') +
            '__' + item_slot.lower().replace(' ', '_'))
# End GenerateTierTag

# Extracts the normalized socket string and item slot string from the given tier tag
def DecodeTierTag(tier_tag: str) -> Tuple[str, str]:
    CheckType(tier_tag, 'tier_tag', str)
    socket_string, item_slot = tier_tag.split('__')
    socket_string = socket_string.replace('_', ' ')
    item_slot = item_slot.replace('_', ' ')
    return NormalizedSocketString(socket_string), string_helper.ToTitleCase(item_slot)
# End DecodeTierTag

# The input is a socket_string, item_slot string pair.
# socket_string is case insensitive and has the following form:
#  - <color><link><color><link><color>...
#  - color is one of: 'R', 'G', 'B','W', 'D', 'A', 'X' (any socket)
#  - link is one of: '', ' ' (equivalent to ''), '-'
#  - sockets are order-insensitive, in so far as changing order maintains socket groups
# item_slot is case insensitive, and is either 'any' or the name a specific item slot.
# Returns a list of rules condition strings, which combine to match the given socket_string.
# Note: 'RGB-X' is equivalent to 'RG B-X' is equivalent to 'R G B-X'
def GenerateClassAndSocketConditions(socket_string: str, item_slot: str) -> List[str]:
    CheckType(socket_string, 'socket_string', str)
    normalized_socket_string = NormalizedSocketString(socket_string)
    if (normalized_socket_string == None):
        raise RuntimeError('Invalid socket string: {}'.format(socket_string))
    # Now we have a string of the form: 'R-X-B G-X W', which translates to the conditions:
    #  - Sockets >= 6RBGW
    #  - SocketGroup >= 3RB
    #  - SocketGroup >= 2G
    #  - SocketGroup >= 1W  # Can be omitted, group size of 1 is covered by Sockets condition
    #
    # Note that these generated conditions do not represent the original socket string
    # exactly.  The above could have matched an item with sockets 'R-B-G R R W'
    #
    # This is an inherent result of design of PoE loot filter conditions. As a more
    # obvious example, consider: 'R-X-X B-X-X'. This translates to:
    #  - Sockets >= 6RB
    #  - SocketGroup >= 3R
    #  - SocketGroup >= 3B
    # This matches an item with sockets 'R-B-G G G G', because we have no way of
    # eliminating a socket group from matching future conditions after it matches one.
    # Separate conditions are always evaluated independently.
    # This should be a seldom-encountered, trivial-impact issue, since by the time players
    # regularly encounter multi-socket-group items, they have the fusings to fix them.

    condition_lines = []
    # First, create the item class condition from the item slot
    item_slot_title_case = string_helper.ToTitleCase(item_slot.lower())
    if (item_slot_title_case != 'Any'):
        if (item_slot_title_case not in consts.kItemSlots):
            raise RuntimeError('Invalid item slot: {}'.format(item_slot))
        # Use 'Weapon' to match 'One Handed Weapon' and 'Two Handed Weapon' (must be singular)
        item_classes = (consts.kWeaponItemClasses if (item_slot_title_case == 'Weapons')
                else [item_slot_title_case])
        condition_lines += ['Class == {}'.format(
                parse_helper.ConvertValuesListToString(item_classes))]
    # Next, create the Sockets condition
    socket_colors = [c for c in normalized_socket_string if (c in kValidSocketColorCharacters)]
    socket_condition_socket_string = (str(len(socket_colors)) +
            ''.join(c for c in socket_colors if c != 'X'))
    condition_lines.append('Sockets >= ' + socket_condition_socket_string)
    # Finally, generate required socket groups
    socket_group_strings = normalized_socket_string.split(' ')
    for socket_group_string in socket_group_strings:
        socket_colors = socket_group_string.split('-')
        # Can skip condition if group size is 1
        if (len(socket_group_string) == 1):
            continue
        socket_group_condition_socket_string = (str(len(socket_colors)) +
                ''.join(c for c in socket_colors if c != 'X'))
        condition_lines.append('SocketGroup >= ' + socket_group_condition_socket_string)
    return condition_lines
# End ParseSocketString
