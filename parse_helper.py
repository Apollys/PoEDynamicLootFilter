'''
General parsing functions:
 - FindFirstMatchingPredicate(s: str, predicate) -> int
 - MakeUniqueId(new_id: str, used_ids) -> str
 - ParseNumberFromString(input_string: str, starting_index: int = 0) -> int

Loot filter related functions:
 - CommentedLine(line: str)
 - UncommentedLine(line: str)
 - IsCommented(line: str) -> bool
 - IsSectionOrGroupDeclaration(line: str) -> bool
 - ParseSectionOrGroupDeclarationLine(line) -> Tuple[bool, str, str]
 - ConvertValuesStringToList(values_string: str) -> List[str]
 - ConvertValuesListToString(values_list: List[str]) -> str
'''

import re
from typing import Dict, List, Tuple

import consts
import simple_parser
from type_checker import CheckType

kShowHideLinePattern = re.compile(r'^\s*#?\s*(Show|Hide)')

# ========================== Generic Helper Methods ==========================

# Given a string and a predicate (function mapping character to bool),
# returns the index of the first character in the string for which
# the predicate returns True.
# Returns -1 if predicate returns False for all characters in the string.
def FindFirstMatchingPredicate(s: str, predicate) -> int:
    CheckType(s, 's', str)
    for i in range(len(s)):
        if (predicate(s[i])): return i
    return -1
# End FindFirstMatchingPredicate()

# If new_id already exists in used_ids, appends "_" followed by increasing
# numeric values until an id is found which does not exist in used_ids.
# Here, used_ids can be any data type for which "some_id in used_ids" works.
def MakeUniqueId(new_id: str, used_ids) -> str:
    CheckType(new_id, 'new_id', str)
    candidate_id: str = new_id
    id_suffix_counter = 0
    while (candidate_id in used_ids):
        candidate_id = new_id + '_' + str(id_suffix_counter)
        id_suffix_counter += 1
    return candidate_id
# End MakeUniqueId()

# Parses the first encountered sequence of consecutive digits as an int.
# For example, 'hello 123 456 world' would yield 123.
# Note: assumes number is purely composed of digits (importantly: non-negative)
def ParseNumberFromString(input_string: str, starting_index: int = 0) -> int:
    number_string = ''
    for c in input_string[starting_index:]:
        if (c.isdigit()):
            number_string += c
        else:
            break
    return int(number_string)
# End ParseNumberFromString

# ==================== Loot Filter Specifc Helper Methods ====================

def CommentedLine(line: str) -> str:
    CheckType(line, 'line', str)
    if (line.strip().startswith('#')):
        return line
    return '# ' + line
# End CommentedLine

def UncommentedLine(line: str) -> str:
    CheckType(line, 'line', str)
    if (line.strip().startswith('# ')):
        return line.replace('# ', '', 1)  # 3rd parameter is max number of replacements
    elif (line.strip().startswith('#')):
        return line.replace('#', '', 1)  # 3rd parameter is max number of replacements
    return line  # already uncommented
# End UncommentedLine

def IsCommented(line: str) -> bool:
    CheckType(line, 'line', str)
    return line.strip().startswith('#')
# End IsCommented

# Returns the index of the Show/Hide line, or None if no such line found
def FindShowHideLineIndex(rule_text_lines: str) -> int:
    for i in reversed(range(len(rule_text_lines))):
        if (re.search(kShowHideLinePattern, rule_text_lines[i])):
            return i
    return None
# End FindTagLineIndex

# Returns True if the given line is a section declaration or section group
# declaration, and False otherwise.
def IsSectionOrGroupDeclaration(line: str) -> bool:
    CheckType(line, 'line', str)
    return bool(consts.kSectionRePattern.search(line))    
# End IsSectionOrGroupDeclaration

# TODO: IsRuleStart should be unnecessary now
# Returns True if the line at the given index marks the start of a rule, else returns False
# The reason this is a lot more complicated than it seems is the following possible scenario:
'''
# Show 3 socketed items
# Show 4 socketed items
# Show
# Sockets >= 3
# SetFontSize 45

'''
# Here, the rule doesn't start until the third line!  The other two are comments,
# and we need to make sure we don't think they're real loot filter code
# The only way to solve this is to parse backwards from the end of the rule if it's commented.
def IsRuleStart(lines: List[str], index: int) -> bool:
    CheckType2(lines, 'lines', list, str)
    CheckType(lines[index], 'lines[index]', str)
    CheckType(index, 'index', int)
    if (not lines[index].startswith('#')):
        return lines[index].startswith('Show') or lines[index].startswith('Hide')
    # Otherwise, find the end of the rule and parse backwards to find its start line
    i: int = index
    while (lines[i] != ''):
        i += 1
    while (i >= index):
        line: str = lines[i]
        if (line.startswith('Show') or line.startswith('Hide') or
                line.startswith('#Show') or line.startswith('#Hide') or
                line.startswith('# Show') or line.startswith('# Hide')):
            # Found the true rule start at i
            return i == index
        i -= 1
    # If somehow we made it back here, there was no rule, just a random comment block
    return False
# End IsRuleStart()

# TODO: ParseShowFlag should be unnecessary now
def ParseShowFlag(lines: List[str]) -> bool:
    CheckType2(lines, 'lines', list, str)
    for line in lines:
        if (line.startswith('#')):
            line = line[1:].strip()
        if (line.startswith('Show')):
            return True
        elif (line.startswith('Hide')):
            return False
    raise RuntimeError(
            'Could not determine if rule is Show or Hide from rule:\n{}'.format('\n'.join(lines)))
# End ParseShowFlag

# Returns (is_section_group, section_id, section_name) triplet
# Example: "# [[1000]] High Level Crafting Bases" -> "1000", "High Level Crafting Bases"
# Or: "# [1234] ILVL 86" -> "1234", "ILVL 86" 
def ParseSectionOrGroupDeclarationLine(line) -> Tuple[bool, str, str]:
    CheckType(line, 'line', str)
    first_opening_bracket_index = -1
    id_start_index = -1
    id_end_index = -1
    name_start_index = -1
    found_opening_bracket = False
    for i in range(len(line)):
        if (first_opening_bracket_index == -1):
            if (line[i] == '['):
                first_opening_bracket_index = i
            continue
        elif (id_start_index == -1):
            if (line[i].isdigit()):
                id_start_index = i
            continue
        elif (id_end_index == -1):
            if (line[i] == ']'):
                id_end_index = i
            continue
        else:  # name_start_index == -1
            if ((line[i] != ']') and (not line[i].isspace())):
                name_start_index = i
                break;
    is_section_group = (id_start_index - first_opening_bracket_index) > 1
    section_id = line[id_start_index : id_end_index]
    section_name = line[name_start_index :]
    return is_section_group, section_id, section_name
# End ParseSectionOrGroupDeclarationLine

# Convert a list of string values to a single string.  For example:
#  - '"Orb of Chaos" "Orb of Alchemy"' -> ['Orb of Chaos', 'Orb of Alchemy']
#  = 'Boots Gloves Helmets' -> ['Boots', 'Gloves', 'Helmets']
# Assumes either all or none of the items in values_string are enclosed in quotes.
def ConvertValuesStringToList(values_string: str) -> List[str]:
    CheckType(values_string, 'values_string', str)
    if ('"' in values_string):  # assume all values are enclosed in quotes
        values_list = simple_parser.ParseEnclosedBy(values_string, '"')
    else:
        values_list = values_string.split(' ')
    return values_list
# End ConvertValuesStringToList

# Convert a list of string values to a single string.  For example:
#  - ['Orb of Chaos', 'Orb of Alchemy'] -> '"Orb of Chaos" "Orb of Alchemy"'
#  = ['Boots', 'Gloves', 'Helmets'] -> 'Boots Gloves Helmets'
# Returned string always either encloses all or none of its values in quotes.
def ConvertValuesListToString(values_list: List[str]) -> str:
    if (any(' ' in s for s in values_list)):
        return '"' + '" "'.join(values_list) + '"'
    return ' '.join(values_list)
# ConvertValuesListToString

# TODO: this shouldn't be needed anymore
# Given the BaseType text line from a loot filter rule, return list of base type strings
# Example: BaseType "Orb of Alchemy" "Orb of Chaos" -> ["Orb of Alchemy", "Orb of Chaos"]
# Also works on the following line formats:
# # BaseType "Orb of Alchemy" "Orb of Chaos"  (commented line)
# BaseType == "Orb of Alchemy" "Orb of Chaos"  (double equals)
# BaseType Alchemy Chaos  (result would be ["Alchemy", "Chaos"])
def ParseBaseTypeLine(line: str) -> List[str]:
    CheckType(line, 'line', str)
    # First remove 'BaseType' and anything before it from line
    start_index = line.find('BaseType') + len('BaseType') + 1
    line = line[start_index:]
    if (line == ''):
        return []
    if ('"' in line):
        start_index = line.find('"')
        end_index = line.rfind('"')
        return line[start_index + 1 : end_index].split('" "')
    # Otherwise, items are just split by spaces
    return line.split(' ')
# End ParseBaseTypeLine

# TODO: I don't think this is used anyhere
# Encloses the string in double quotes if it contains a space or single quote,
# otherwise just returns the given string.  Note: does not check for double quotes in string.
def QuoteStringIfRequired(input_string: str) -> str:
    if ((" " in input_string) or ("'" in input_string)):
        return '"' + input_string + '"'
    return input_string
# End QuoteStringIfRequired

# TODO: shouldn't use this anymore
# Given a list of strings, joins the strings with a space,
# and additionally encloses any string that contains a single quote or space in ""
def JoinParams(params_list: List[str]) -> str:
    CheckType2(params_list, 'params_list', list, str)
    return ' '.join(QuoteStringIfRequired(param) for param in params_list)
# End JoinParams

