import string

from type_checker import CheckType

# TODO: write unit tests.
# Creates a normalized tier tag to be used for the rule corresponding to the given parameters.
# Examples:
#  - sorcerers_boots__84__100__rare
#  - steel_ring__86__100__any
# Case is converted to lower, non-alphanumeric characters are removed, and spaces are converted to
# underscores.  Properties are separated by double underscores.
def NormalizedBaseTypeTierTag(base_type: str, min_ilvl: int, max_ilvl: int, rare_only_flag: bool) -> str:
    CheckType(base_type, 'base_type', str)
    CheckType(min_ilvl, 'min_ilvl', int)
    CheckType(max_ilvl, 'mimax_ilvlvl', int)
    CheckType(rare_only_flag, 'rare_only_flag', bool)
    normalized_base_type_tag = ''
    for c in base_type.replace(' ', '_'):
        if (c in string.ascii_letters + string.digits + '_'):
            normalized_base_type_tag += c.lower()
    normalized_base_type_tag += '__{}__{}__'.format(min_ilvl, max_ilvl)
    normalized_base_type_tag += 'rare' if rare_only_flag else 'any'
    return normalized_base_type_tag
# End NormalizedBaseTypeTag