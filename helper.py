from typing import Dict, List, Tuple

from type_checker import CheckType

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

# ==================== Loot Filter Specifc Helper Methods ====================

# Returns True if the given line marks the start of a rule, else returns False
def IsRuleStart(line: str) -> bool:
    CheckType(line, 'line', str)
    return (line.startswith('Show') or line.startswith('Hide') or
            line.startswith('#Show') or line.startswith('#Hide') or
            line.startswith('# Show') or line.startswith('# Hide'))
# End IsRuleStart()

# Given the BaseType text line from a loot filter rule, return list of base type strings
# Example: BaseType "Orb of Alchemy" "Orb of Chaos" -> ["Orb of Alchemy", "Orb of Chaos"]
# Also works on the following line formats:
# # BaseType "Orb of Alchemy" "Orb of Chaos"  (commented line)
# BaseType == "Orb of Alchemy" "Orb of Chaos"  (double equals)
# BaseType Alchemy Chaos  (result would be ["Alchemy", "Chaos"])
def ParseBaseTypeLine(line: str) -> List[str]:
    CheckType(line, 'line', str)
    if ('"' in line):
        start_index = line.find('"')
        end_index = line.rfind('"')
        return line[start_index + 1 : end_index].split('" "')
    # Otherwise, items are just split by spaces, but we have to be careful
    # about an extra space in comment: e.g. "# BaseType A B C"
    start_index = line.find('BaseType ') + len('BaseType ')
    return line[start_index :].split(' ')
# End ParseBaseTypeLine

