import string

from type_checker import CheckType

# Note: does not convert uppercase characters to lowercase.
# If that is desired, pass in s.lower() to this function.
def ToTitleCase(s: str):
    CheckType(s, 's', str)
    result_string = ''
    word_start_flag = True
    for c in s:
        if (c in string.ascii_letters + '\'"'):
            result_string += c.upper() if word_start_flag else c
            word_start_flag = False
        else:
            result_string += c
            word_start_flag = True
    return result_string
# End ToTitleCase