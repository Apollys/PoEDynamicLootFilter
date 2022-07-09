'''
General parsing functions:
 - FindElement(element, collection) -> int
 - IsSubstringInLines(s: str, lines: List[str] or str) -> bool
 - FindFirstMatchingPredicate(s: str, predicate) -> int
 - MakeUniqueId(new_id: str, used_ids) -> str
 - ParseNumberFromString(input_string: str, starting_index: int = 0) -> int

Loot filter related functions:
 - CommentedLine(line: str)
 - UncommentedLine(line: str)
 - IsCommented(line: str) -> bool
 - IsSectionOrGroupDeclaration(line: str) -> bool
 - ParseSectionOrGroupDeclarationLine(line) -> Tuple[bool, str, str]
 - FindShowHideLineIndex(rule_text_lines: List[str]) -> int
 - ParseRuleLineGeneric(line: str) -> Tuple[str, str, List[str]]
 - ParseTypeTierTags(rule_text_lines: List[str]) -> Tuple(str, str)
 - ConvertValuesStringToList(values_string: str) -> List[str]
 - ConvertValuesListToString(values_list: List[str]) -> str
'''

import re
from typing import List, Tuple

import consts
import simple_parser
from type_checker import CheckType

kShowHideLinePattern = re.compile(r'^\s*#?\s*(Show|Hide)')

# ========================== Generic Helper Methods ==========================

# Returns the index of the element in the collection if present,
# or None if the element is not present.
# TODO: Write unit tests for this.
def FindElement(element, collection) -> int:
    for i, value in enumerate(collection):
        if (value == element):
            return i
    return None
# End FindElement

# Returns true if s is a substring of any of the strings in lines.
def IsSubstringInLines(s: str, lines: List[str] or str) -> bool:
    CheckType(s, 's', str)
    if (isinstance(lines, str)):
        return s in lines
    CheckType(lines, 'lines', list, str)
    for line in lines:
        if s in line:
            return True
    return False
# End IsSubstringInLines

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

# Returns True if the given line is a section declaration or section group
# declaration, and False otherwise.
def IsSectionOrGroupDeclaration(line: str) -> bool:
    CheckType(line, 'line', str)
    return bool(consts.kSectionRePattern.search(line))
# End IsSectionOrGroupDeclaration

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

# Returns the index of the Show/Hide line, or None if no such line found.
# Robust to the rule having a header comment starting with 'Show'/'Hide'.
def FindShowHideLineIndex(rule_text_lines: List[str] or str) -> int:
    if (isinstance(rule_text_lines, str)):
        rule_text_lines = rule_text_lines.split('\n')
    CheckType(rule_text_lines, 'rule_text_lines', list, str)
    for i in reversed(range(len(rule_text_lines))):
        if (re.search(kShowHideLinePattern, rule_text_lines[i])):
            return i
    return None
# End FindShowHideLineIndex

# A generic rule line is of the form: <keyword> <optional: operator> <values>
# This will be parsed as the tuple (keyword, operator_string, values_list).
def ParseRuleLineGeneric(line: str) -> Tuple[str, str, List[str]]:
    CheckType(line, 'line', str)
    # Ensure line is uncommented and strip
    line = UncommentedLine(line).strip()
    # Split into keyword, (optional) op_string, values_string
    if (' ' not in line):
        keyword = line
        return keyword, '', []
    keyword, op_and_values = line.split(' ', maxsplit=1)
    op_string = ''
    values_string = ''
    # Parse and update op_string if input line contains an operator
    split_result = op_and_values.split(' ', maxsplit=1)
    if (split_result[0] in consts.kOperatorMap):
        op_string = split_result[0]
        if (len(split_result) > 1):
            values_string = split_result[1]
    else:  # no operator
        values_string = op_and_values
    return keyword, op_string, ConvertValuesStringToList(values_string)
# End ParseRuleLineGeneric

# Returns type_tag, tier_tag if rule has tags, else None, None.
def ParseTypeTierTags(rule_text_lines: List[str]) -> Tuple[str, str]:
    CheckType(rule_text_lines, 'rule_text_lines', list, str)
    tag_line_index = FindShowHideLineIndex(rule_text_lines)
    if (tag_line_index == -1):
        return None, None
    tag_line = rule_text_lines[tag_line_index]
    success, tag_list = simple_parser.ParseFromTemplate(
        tag_line + ' ', template='{~}$type->{} $tier->{} {~}')
    return tuple(tag_list) if success else None
# End ParseTypeTierTags

# Convert a list of string values to a single string.  For example:
#  - '"Orb of Chaos" "Orb of Alchemy"' -> ['Orb of Chaos', 'Orb of Alchemy']
#  = 'Boots Gloves Helmets' -> ['Boots', 'Gloves', 'Helmets']
# Assumes either all or none of the items in values_string are enclosed in quotes.
def ConvertValuesStringToList(values_string: str) -> List[str]:
    CheckType(values_string, 'values_string', str)
    if (len(values_string) == 0):
        return []
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
