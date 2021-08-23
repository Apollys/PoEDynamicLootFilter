from typing import Dict, List, Tuple

import consts
from type_checker import CheckType

# ========================== Generic Helper Methods ==========================

# Read lines of a file to a list of strings
# Safe against file not existing
def ReadFile(fullpath: str) -> List[str]:
    CheckType(fullpath, 'fullpath', str)
    try:
        with open(fullpath) as input_file:
            return input_file.readlines()
    except FileNotFoundError:
        return []
# End ReadFile

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

# Note: assumes number is purely composed of digits, i.e. non-negative
def ParseNumberFromString(input_string: str, starting_index: int = 0) -> int:
    number_string = ''
    for c in input_string[starting_index:]:
        if (c.isdigit()):
            number_string += c
        else:
            break
    return int(number_string)

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

# Returns True if the given line is a section declaration or section group
# declaration, and False otherwise.
def IsSectionOrGroupDeclaration(line: str) -> bool:
    CheckType(line, 'line', str)
    return bool(consts.kSectionRePattern.search(line))    

# Returns True if the given line marks the start of a rule, else returns False
def IsRuleStart(line: str) -> bool:
    CheckType(line, 'line', str)
    return (line.startswith('Show') or line.startswith('Hide') or
            line.startswith('#Show') or line.startswith('#Hide') or
            line.startswith('# Show') or line.startswith('# Hide'))
# End IsRuleStart()

# Handles both sections and section groups (single and double bracket ids)
# Returns (is_section_group, section_id, section_name) triplet
# Example: "# [[1000]] High Level Crafting Bases" -> "1000", "High Level Crafting Bases"
# Or: "# [1234] ILVL 86" -> "1234", "ILVL 86" 
def ParseSectionDeclarationLine(line) -> Tuple[bool, str, str]:
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
# End ParseSectionDeclarationLine

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

