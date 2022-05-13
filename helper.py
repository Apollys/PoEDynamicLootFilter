import os
import re
from typing import Dict, List, Tuple

import consts
from type_checker import CheckType, CheckType2

# ========================== Generic Helper Methods ==========================

# Read lines of a file to a list of strings
# Safe against file not existing
def ReadFile(fullpath: str, retain_newlines: bool = True) -> List[str]:
    CheckType(fullpath, 'fullpath', str)
    CheckType(retain_newlines, 'retain_newlines', bool)
    try:
        with open(fullpath) as input_file:
            lines = input_file.readlines()
        if (not retain_newlines):
            for i in range(len(lines)):
                lines[i] = lines[i].rstrip('\n')
        return lines
    except FileNotFoundError:
        return []
# End ReadFile

# Writes data to the file determined by fullpath
# Overwrites the given file if it already exists
# If data is a non-string iterable type, then it is written as newline-separated items
# Otherwise, str(data) is written directly to file
# Safe against directory not existing (creates directory if missing)
def WriteToFile(data, fullpath: str):
    parent_directory = os.path.dirname(fullpath)
    if (parent_directory != ''):
        os.makedirs(parent_directory, exist_ok = True)
    with open(fullpath, 'w') as f:
        if (isinstance(data, str)):
            f.write(data)
        else:
            try:
                iter(data)
                data_list = list(data)
                f.write('\n'.join(str(x) for x in data_list))
            except TypeError:
                f.write(str(data))
# End WriteToFile

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

kTagLinePattern = re.compile(r'^\s*#?\s*(Show|Hide|Disable)')

# Finds the index of the Show/Hide/Disable line, or returns -1 if no such line found
def FindTagLineIndex(rule_text_lines: str) -> int:
    for i in reversed(range(len(rule_text_lines))):
        if (re.search(kTagLinePattern, rule_text_lines[i])):
            return i
    return -1
# End FindTagLineIndex

# Returns True if the given line is a section declaration or section group
# declaration, and False otherwise.
def IsSectionOrGroupDeclaration(line: str) -> bool:
    CheckType(line, 'line', str)
    return bool(consts.kSectionRePattern.search(line))    

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

# Copied from above, for archnemesis line
def ParseArchnemesisModLine(line: str) -> List[str]:
    CheckType(line, 'line', str)
    # First remove 'ArchnemesisMod' and anything before it from line
    start_index = line.find('ArchnemesisMod') + len('ArchnemesisMod') + 1
    line = line[start_index:]
    if (line == ''):
        return []
    if ('"' in line):
        start_index = line.find('"')
        end_index = line.rfind('"')
        return line[start_index + 1 : end_index].split('" "')
    # Otherwise, items are just split by spaces
    return line.split(' ')
# End ParseArchnemesisModLine

# Encloses the string in double quotes if it contains a space or single quote,
# otherwise just returns the given string.  Note: does not check for double quotes in string.
def QuoteStringIfRequired(input_string: str) -> str:
    if ((" " in input_string) or ("'" in input_string)):
        return '"' + input_string + '"'
    return input_string
# End QuoteStringIfRequired

# Given a list of strings, joins the strings with a space,
# and additionally encloses any string that contains a single quote or space in ""
def JoinParams(params_list: List[str]) -> str:
    CheckType2(params_list, 'params_list', list, str)
    return ' '.join(QuoteStringIfRequired(param) for param in params_list)
# End JoinParams

