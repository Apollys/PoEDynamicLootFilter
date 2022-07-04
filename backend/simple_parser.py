'''
 - ParseFromTemplate(s: str, template: str) -> Tuple[bool, List[str]]
 - ParseEnclosedBy(line: str, start_seq: str, end_seq: str = None) -> List[str]
 - IsInt(s: str or int) -> bool
 - ParseInts(line: str or int) -> List[int]
 - ParseValueDynamic(s: Any) -> Any
'''

from typing import List, Tuple, Any

from type_checker import CheckType

kWildcardMatchString = '{}'
kWildcardIgnoreString = '{~}'
kTerminationChar = '*'

# Returns (is_wildcard: bool, is_match: bool, wildcard_length: int) triplet
def IsWildcard(template: str, index: int) -> Tuple[bool, bool, int]:
    CheckType(template, 'template', str)
    CheckType(index, 'index', int)
    if (template[index :].startswith(kWildcardMatchString)):
        return True, True, len(kWildcardMatchString)
    elif (template[index :].startswith(kWildcardIgnoreString)):
        return True, False, len(kWildcardIgnoreString)
    return False, False, 0
# End IsWildcard

# Input string to parse must not contain "wildcards": '{}' or '{~}'.
# Neither input nor template string may contain '*' (reserved as a termination char).
# Wildcards in template string indicate to match a sequence of characters:
#  - '{}' keeps the matched substring as part of the parse result
#  - '{~}' discards the matched substring
# Wildcards can match the empty string. Consecutive wildcards are not permitted.
# Returns the pair: parse_success, parse_result_list
# Example: ParseFromTemplate("abc:xyz", "{}:{~}") -> true, ["abc"]
def ParseFromTemplate(s: str, template: str) -> Tuple[bool, List[str]]:
    CheckType(s, 's', str)
    CheckType(template, 'template', str)
    # The logic is much simpler if we append an identical character to both strings,
    # so we don't have to add special conditions for end of string.
    s += kTerminationChar
    template += kTerminationChar
    s_index: int = 0
    template_index: int = 0
    token_list = []
    in_token = False
    current_token = ''
    keep_token = False
    while (s_index < len(s)):
        is_wildcard, is_match, wc_length = IsWildcard(template, template_index)
        # Case 1: encountered new token start
        if (is_wildcard):
            # Start new token
            in_token = True
            keep_token = is_match
            template_index += wc_length
        # Case 2: characters match -> end token if in token
        elif ((template_index < len(template)) and (s[s_index] == template[template_index])):
            if (in_token):
                if (keep_token):
                    token_list.append(current_token)
                in_token = False
                current_token = ''
            # Whether inside or outside of token, characters matched so we increment indices
            s_index += 1
            template_index += 1
        # Case 3: characters don't match and we're already in token -> swallow up character in s
        elif (in_token):
            current_token += s[s_index]
            s_index += 1
        # Case 4: not in token, characters don't match, and not starting new token - Error
        else:
            return False, []
    # If we're not at the end of *both* strings here, it was a mismatch
    if (template_index < len(template)):
        return False, []
    # Otherwise, we have a successful match - add last token if needed
    if (in_token and keep_token):
        token_list.append(current_token)
    return True, token_list
# End ParseFromTemplate

# Example: parsing the string 'BaseType "Leather Belt" "Two-Stone Ring" "Agate Amulet"'
# with start_seq = '"' yields ['Leather Belt', 'Two-Stone Ring', 'Agate Amulet'].
def ParseEnclosedBy(line: str, start_seq: str, end_seq: str = None) -> List[str]:
    if (end_seq == None): end_seq = start_seq
    CheckType(line, 'line', str)
    CheckType(start_seq, 'start_seq', str)
    CheckType(end_seq, 'end_seq', str)
    index = 0
    token_list = []
    while (0 <= index < len(line)):
        start_find_result = line.find(start_seq, index)
        if (start_find_result == -1): break
        start_index = start_find_result + len(start_seq)
        end_find_result = line.find(end_seq, start_index + 1)
        if (end_find_result == -1): break
        end_index = end_find_result
        token_list.append(line[start_index : end_index])
        index = end_index + 1
    return token_list
# End ParseEnclosedBy

def IsInt(s: str or int) -> bool:
    if (isinstance(s, int)):
        return s
    CheckType(s, 's', str)
    try:
        int(s)
    except:
        return False
    return True
# End IsInt

def ParseInts(line: str or int) -> List[int]:
    if (isinstance(line, int)):
        return [line]
    CheckType(line, 'line', str)
    parsed_ints = []
    current_int_string = ''
    # Add non-digit to end of line to handle last integer uniformly
    for c in line + ' ':
        if ((len(current_int_string) > 0) and not c.isdigit()):
                parsed_ints.append(int(current_int_string))
                current_int_string = ''
        elif c.isdigit():
            current_int_string += c
    return parsed_ints
# End ParseInts

# Attempts to parse the string as a value of various types, and returns the parsed value:
#  - If the string's is True/False/true/false, returns bool
#  - If the string can be parsed as an int, returns int
#  - Otherwise, returns the input string
# If the input value is not a string, returns the input value directly.
def ParseValueDynamic(s: Any) -> Any:
    if (not isinstance(s, str)):
        return s
    if (s in ('True', 'False', 'true', 'false')):
        return s.lower() == 'true'
    elif (IsInt(s)):
        return int(s)
    return s
# End ParseValueDynamic