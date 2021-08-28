from typing import List, Tuple

kWildcardMatchString = '{}'
kWildcardIgnoreString = '{~}'

# Returns (is_wildcard: bool, is_match: bool, wildcard_length: int) triplet
def IsWildcard(template: str, index: int) -> Tuple[bool, bool, int]:
    if (template[index :].startswith(kWildcardMatchString)):
        return True, True, len(kWildcardMatchString)
    elif (template[index :].startswith(kWildcardIgnoreString)):
        return True, False, len(kWildcardIgnoreString)
    return False, False, 0
# End IsWildcard

# Strings must not contain reserved kWildcardMatchChar kWildcardIgnoreChar
# other than as indicators in the template string to match/ignore a sequence of characters
# Returns (parse_success: bool, parse_result_list: List[str]) pair
def ParseFromTemplate(s: str, template: str) -> Tuple[bool, List[str]]:
    s_index: int = 0
    template_index: int = 0
    token_list = []
    current_token = ''
    in_token = False
    keep_token = False
    while (s_index < len(s)):
        is_wildcard, is_match, wc_length = IsWildcard(template, template_index)
        #print('s[{}] = {}, template[{}] = {}, current_token = {}'.format(
         #       s_index, s[s_index], template_index, template[template_index], current_token))
        # Case 1: characters match
        if (s[s_index] == template[template_index]):
            # Characters match while inside of token -> end current token
            if (in_token):
                if (keep_token):
                    token_list.append(current_token)
                in_token = False
            # Whether inside or outside of token, characters matched so we increment indices
            s_index += 1
            template_index += 1
            continue
        # Case 2: characters don't match, but it doesn't matter because we're already in token
        elif (in_token):
            current_token += s[s_index]
            s_index += 1
        # Case 3: characters don't match, not in token, but encountered new token start
        elif (is_wildcard):
            # Start new token
            in_token = True
            keep_token = is_match
            current_token = s[s_index]
            s_index += 1
            template_index += wc_length
            # If this token is the end of the template string, just swallow up the rest of s
            if (template_index == len(template)):
                current_token = s[s_index - 1 :]
                break
        # Case 4: characters don't match, not in token, can't start new token - Error
        else:
            return False, []
    # If loop terminated by reaching end of s, but template still has unmatched characters, Error
    # Exception: if we're at the end of the template string, and the charater there is '~',
    # then it is allowed to match the empty string, so the result is valid
    if (template_index != len(template)):
        is_wildcard, is_match, wc_length = IsWildcard(template, template_index)
        if (is_wildcard and ((template_index + wc_length) == len(template))):
            keep_token = is_match
            if (keep_token):
                token_list.append('')
        else:
            return False, []
    # Add last token if needed
    if (in_token and keep_token):
        token_list.append(current_token)
    return True, token_list
# End ParseFromTemplate

def ParseEnclosedBy(line: str, start_seq: str, end_seq: str = None) -> List[str]:
    if (end_seq == None): end_seq = start_seq
    index = 0
    token_list = []
    while (0 <= index < len(line)):
        start_index = line.find(start_seq, index) + len(start_seq)
        end_index = line.find(end_seq, start_index + 1)
        token_list.append(line[start_index : end_index])
        index = end_index + 1
    return token_list
# End ParseEnclosedBy

def IsInt(s: str) -> bool:
    try:
        int(s)
    except:
        return False
    return True
# End IsInt

def ParseInts(line: str) -> List[int]:
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

def ParseFromTemplateTest():
    line1 = 'Show # $type->decorator->craftingrare $tier->raredecoratorgear '
    line2 = 'Show # $type->decorator->craftingrare $tier->raredecoratorgear $other_garbage lalal'
    template = 'Show {~}$type->{} $tier->{} {~}'
    success, result = ParseFromTemplate(line1 + ' ', template)
    print(result)
    success, result = ParseFromTemplate(line2 + ' ', template)
    print(result)
    result == ['...', 'decorator->craftingrare', 'raredecoratorgear', '...']
    
    
def ParseEnclosedByTest():
    line = 'BaseType "Leather Belt" "Two-Stone Ring" "Agate Amulet"'
    result = ParseEnclosedBy(line, '"', '"')
    print(result)
    result == ['Leather Belt', 'Two-Stone Ring', 'Agate Amulet']

def ParseIntsTest():
    line = 'asdf45 re2 7432'
    result = ParseInts(line)
    print(result)
    result == [45, 2, 7432]
    
# ParseFromTemplateTest()
# ParseEnclosedByTest()
# ParseIntsTest()
