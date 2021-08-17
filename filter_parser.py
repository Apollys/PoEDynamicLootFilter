import re

from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Tuple

kInputLootFilterFilename = 'AABrandLeaguestart.filter'
kOutputLootFilterFilename = 'output.filter'
kLogFilename = 'log.log'

kCurrencyTierNames = {'t1' : 't1exalted',
                      't2' : 't2divine',
                      't3' : 't3annul',
                      't4' : 't4chaos',
                      't5' : 't5alchemy',
                      't6' : 't6chrom',
                      't7' : 't7chance',
                      't8' : 't8trans',
                      't9' : 't9armour'}

# === Helper Functions ===

def InitializeLog():
    open(kLogFilename, 'w').close()

# Used to log any errors, warnings, or debug information
# item can be a string or anything convertible to string
def Log(item):
    message: str = item if isinstance(item, str) else str(item)
    with open(kLogFilename, 'a') as log_file:
        log_file.write(message + '\n')
# End Log()
        
# Logs error and raises exception if variable is not an instance of required type
# Note: can use a tuple of types for required_type to give multiple options
def CheckType(variable, variable_name: str, required_type):
    if not isinstance(variable, required_type):
        required_type_name = required_type.__name__ if type(required_type) == type else \
                ' or '.join(t.__name__ for t in required_type)
        error_message: str = '{} has type: {}; required type: {}'.format(
                variable_name, type(variable).__name__, required_type_name)
        Log('TypeError: ' + error_message)
        raise TypeError(error_message)
# End CheckType()

def FindFirstMatchingPredicate(s: str, predicate) -> int:
    for i in range(len(s)):
        if (predicate(s[i])): return i
    return -1

# Here, used_ids can be any data type for which "some_id in used_ids" works
def MakeUniqueId(new_id: str, used_ids) -> str:
    CheckType(new_id, 'new_id', str)
    candidate_id: str = new_id
    id_suffix_counter = 0
    while (candidate_id in used_ids):
        candidate_id = new_id + '_' + str(id_suffix_counter)
        id_suffix_counter += 1
    return candidate_id
    
def IsRuleStart(line: str) -> bool:
    CheckType(line, 'line', str)
    return (line.startswith('Show') or line.startswith('Hide') or
            line.startswith('#Show') or line.startswith('#Hide') or
            line.startswith('# Show') or line.startswith('# Hide'))
# End IsRuleStart()
        

# -----------------------------------------------------------------------------

class RuleVisibility(Enum):
    kShow = 1
    kHide = 2
    kDisable = 3  # rule is commented out
    kUnknown = 4

# -----------------------------------------------------------------------------


class LootFilterRule:
    '''
    Member variables:
     - self.text_lines: List[str]
     - self.start_line_index: int - line index of this rule in the original filter file
     - self.visibility: RuleVisibility
     - self.type: str - identifier found after "$type->" in the first line of the rule
     - self.tier: str - identifier found after "$tier->" in the first line of the rule
     - self.base_type_list: List[str]
       - Note: not all rules must have BaseType, so base_type_list may be empty
     - self.base_type_line_index: int - index into self.text_lines (not full loot filter)
    '''

    def __init__(self, rule_text_lines: List[str], start_line_index: int):
        CheckType(rule_text_lines, 'rule_text_lines', list)
        CheckType(start_line_index, 'start_line_index', int)
        if (len(rule_text_lines) == 0):
            Log('Error: emtpy rule found starting on line {} of loot filter'.format(
                    start_line_index + 1))
        self.text_lines = rule_text_lines
        self.start_line_index = start_line_index  # index in full loot filter file
        # Parse rule visibility
        self.visibility = RuleVisibility.kUnknown
        if (rule_text_lines[0].startswith('Show')):
            self.visibility = RuleVisibility.kShow
        elif (rule_text_lines[0].startswith('Hide')):
            self.visibility = RuleVisibility.kHide
        elif (all(line.startswith('#') for line in rule_text_lines)):
            self.visibility = RuleVisibility.kDisable
        else:
            Log(('Warning: unable to determine rule visibility for rule starting on line {}'
                    ' of loot filter').format(start_line_index + 1))
        # Every rule has a "$type" and "$tier" attribute on the first line, for example:
        # Show # $type->currency $tier->t1exalted
        kTypeIdentifier = '$type->'
        kTierIdentifier = '$tier->'
        first_line: str = rule_text_lines[0] + ' '  # add space so parsing is uniform
        type_start_index = first_line.find(kTypeIdentifier) + len(kTypeIdentifier)
        type_end_index = first_line.find(' ', type_start_index)
        tier_start_index = first_line.find(kTierIdentifier) + len(kTierIdentifier)
        tier_end_index = first_line.find(' ', tier_start_index)
        self.type: str = first_line[type_start_index : type_end_index]
        self.tier: str = first_line[tier_start_index : tier_end_index]
        # Parse base type list
        # Note - not all rules may have a base type, in which case base type list is empty
        self.base_type_list = []
        self.base_type_line_index = -1
        for i in range(len(self.text_lines)):
            line: str = self.text_lines[i]
            if (line.startswith('BaseType') or line.startswith('#BaseType') or
                    line.startswith('# BaseType')):
                self.base_type_line_index = i
                self.base_type_list = self.ParseBaseTypeLine(line)
        # TODO: parse size, color, etc...
        
    def __repr__(self):
        return '\n'.join(self.text_lines)
        
    def GetVisibility(self) -> RuleVisibility:
        return self.visibility
    
    def SetVisibility(self, visibility: RuleVisibility) -> None:
        CheckType(visibility, 'visibility', RuleVisibility)
        if (self.visibility == visibility): return
        # Comment to disable
        if (visibility == RuleVisibility.kDisable):
            for i in range(len(self.text_lines)):
                self.text_lines[i] = '# ' + self.text_lines[i]
            self.visibility = visibility
            return
        # Uncomment if currently commented (disabled)
        if (self.visibility == RuleVisibility.kDisable):
            # Handle "# Show" and "#Show" comment styles uniformly
            comment_prefix_length = FindFirstMatchingPredicate(self.text_lines[0], str.isalnum)
            for i in range(len(self.text_lines)):
                self.text_lines[i] = self.text_lines[i][comment_prefix_length :]
        # Toggle Show/Hide
        if ((visibility == RuleVisibility.kShow) and self.text_lines[0].startswith('Hide')):
            self.text_lines[0] = 'Show' + self.text_lines[0][4:]
        elif ((visibility == RuleVisibility.kHide) and self.text_lines[0].startswith('Show')):
            self.text_lines[0] = 'Hide' + self.text_lines[0][4:]
        self.visibility = visibility
    
    def AddBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        if (base_type_name in self.base_type_list):
            return
        self.base_type_list.append(base_type_name)
        original_base_type_line = self.text_lines[self.base_type_line_index]
        self.text_lines[self.base_type_line_index] = \
                self.text_lines[self.base_type_line_index] + ' "' + base_type_name + '"'
    # End AddBaseType()
    
    def RemoveBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        if (base_type_name not in self.base_type_list):
            Log('Warning: requested to remove BaseType ' + base_type_name + ' from rule "' + 
                    self.text_lines[0] + '", but given BaseType is not in this rule')
            return
        self.base_type_list.remove(base_type_name)
        # Potential issue: what if base type list is empty now?
        index = self.base_type_line_index  # for convenience
        quoted_base_type_name = '"' + base_type_name + '"'
        if (quoted_base_type_name in self.text_lines[self.base_type_line_index]):
            self.text_lines[index] = \
                    self.text_lines[index].replace(' ' + quoted_base_type_name, '')
        else:
            self.text_lines[index] = \
                    self.text_lines[index].replace(' ' + base_type_name, '')
    # End RemoveBaseType()
        
    def GetSize(self) -> int:
        pass
        
    def SetSize(self, size: int) -> None:
        pass
        
    def GetRuleTextLines(self) -> List[str]:
        return self.text_lines
    
    # ======================= Private Helper Methods =======================
    
    def ParseBaseTypeLine(self, line: str) -> List[str]:
        if ('"' in line):
            start_index = line.find('"')
            end_index = line.rfind('"')
            return line[start_index + 1 : end_index].split('" "')
        # Otherwise, items are just split by spaces, but we have to be careful
        # about an extra space in comment: e.g. "# BaseType A B C"
        start_index = line.find('BaseType ') + len('BaseType ')
        return line[start_index :].split(' ')
            

# -----------------------------------------------------------------------------


class LootFilter:
    '''
    Member variables:
     - self.text_lines: List[str]
     - self.section_map: OrderedDict[id: str, name: str]
     - self.inverse_section_map: Dict[name: str, id: str]
     - self.rules_start_line_index: int
     - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
     - self.type_tier_rule_map: 2d dict which allows you to access rules by type and tier
       Example: self.type_tier_rule_map['currency']['t1']  
                    -> list of rules of type 'currency' and tier 't1'
    '''

    # ======================= Public API =======================
    
    # Construct LootFilter object, parsing the given loot filter file
    def __init__(self, input_filename: str):
        CheckType(input_filename, 'input_filename', str)
        self.ParseLootFilterFile(input_filename)
        
    # Saves a backup first if output_filename == input_filename
    def SaveToFile(self, output_filename: str):
        CheckType(output_filename, 'output_filename', str)
        with open(output_filename, 'w') as output_file:
            line_index: int = 0
            while (line_index < len(self.text_lines)):
                line: str = self.text_lines[line_index]
                # If not a new rule start, just write input line back out
                if (not IsRuleStart(line)):
                    output_file.write(line + '\n')
                    line_index += 1
                # Otherwise is a new rule - write out the rule from line_index_rule_map
                else:  # IsRuleStart(line)
                    rule = self.line_index_rule_map[line_index]
                    output_file.write(str(rule) + '\n')
                    line_index += len(rule.text_lines)
    # End SaveToFile()
    
    def GetRulesByTypeTier(self, type_name: str, tier_name: str) -> List[LootFilterRule]:
        CheckType(type_name, 'type_name', str)
        CheckType(tier_name, 'tier_name', str)
        return self.type_tier_rule_map[type_name][tier_name]
       
    def ContainsSection(self, section_name: str) -> bool:
        CheckType(section_name, 'section_name', str)
        return section_name in self.inverse_section_map
    
    def ContainsSectionId(self, section_id: str) -> bool:
        CheckType(section_id, 'section_id', str)
        return section_id in self.section_map
    
    def GetSectionId(self, section_name: str) -> str:
        CheckType(section_name, 'section_name', str)
        return self.inverse_section_map[section_name]
    
    def GetSectionName(self, section_id: str) -> str:
        CheckType(section_id, 'section_id', str)
        return self.section_map[section_id]

    # Returns a list of section names containing all the given keywords (case insensitive)
    # keywords must either be of type List[str] or a single str
    def SearchSectionNames(self, keywords) -> List[str]:
        CheckType(keywords, 'keywords', (str, list))
        # Make keywords into a list of strings if input was a single keyword
        if isinstance(keywords, str):
            keywords = [keywords]
        matching_section_names: List[str] = []
        for section_name in self.inverse_section_map:
            contains_all_keywords = all(
                    keyword.lower() in section_name.lower() for keyword in keywords)
            if (contains_all_keywords):
                matching_section_names.append(section_name)
        return matching_section_names
    
    def GetSectionRules(self, section_name: str) -> List[LootFilterRule]:
        CheckType(section_name, 'section_name', str)
        section_id: str = self.inverse_section_map[section_name]
        return self.section_rule_map[section_id]
    
    def ChangeRuleVisibility(self, section_name: str, rule_index: int,
                             visibility: RuleVisibility) -> None:
        pass
    
    # ======================= Private Helper Methods =======================
    
    def ParseLootFilterFile(self, loot_filter_filename: str) -> None:
        CheckType(loot_filter_filename, 'loot_filter_filename', str)      
        self.text_lines: List[str] = []
        with open(loot_filter_filename) as loot_filter_file:
            for line in loot_filter_file:
                self.text_lines.append(line.strip())
        # Ensure there is a blank line at the end to make parsing algorithms cleaner
        if (self.text_lines[-1] != ''):
            self.text_lines.append('')
        self.ParseLootFilterRules(self.text_lines)
    # End ParseLootFilterFile()
    
    def FindRulesStartIndex(self, loot_filter_lines: List[str]) -> int:
        CheckType(loot_filter_lines, 'loot_filter_lines', list)
        found_table_of_contents: bool = False
        for line_index in range(len(loot_filter_lines)):
            line: str = loot_filter_lines[line_index]
            if ('[WELCOME] TABLE OF CONTENTS' in line):
                found_table_of_contents = True
            elif(not found_table_of_contents):
                continue
            # Blank line indicates end of table of contents
            elif (line == ''):
                return line_index + 1
        return -1  # never found table of contents
    
    # Handles both sections and section groups (single and double bracket ids)
    # Returns is_section_group, section_id, section_name triplet
    # Example: "# [[1000]] High Level Crafting Bases" -> "1000", "High Level Crafting Bases"
    # Or: "# [1234] ILVL 86" -> "1234", "ILVL 86" 
    def ParseSectionDeclarationLine(self, line) -> Tuple[bool, str, str]:
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
    
    def ParseLootFilterRules(self, loot_filter_lines: List[str]) -> None:
        '''
        This function parses the rules of the loot filter into the following data structures:
         - self.section_map: OrderedDict[id: str, name: str]
         - self.inverse_section_map: Dict[name: str, id: str]
         - self.rules_start_line_index: int
         - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
         - self.type_tier_rule_map: 2d dict which allows you to access rules by type and tier
           Example: self.type_tier_rule_map['currency']['t1']  
                        -> list of rules of type 'currency' and tier 't1'
        '''
        CheckType(loot_filter_lines, 'loot_filter_lines', list)
        # Initialize data structures to store parsed data
        self.section_map: OrderedDict[str, str] = {}  # maps ids to names
        self.inverse_section_map: Dict[str, str] = {}  # maps names to ids
        self.section_rule_map: OrderedDict[str, List[LootFilterRule]] = OrderedDict()
        self.line_index_rule_map: OrderedDict[int, LootFilterRule] = OrderedDict()
        self.type_tier_rule_map = {}
        # Set up parsing loop
        section_re_pattern = re.compile(r'\[\d+\]+ .*')
        self.rules_start_line_index: int = self.FindRulesStartIndex(loot_filter_lines)
        in_rule: bool = False
        current_rule_lines: List[str] = []
        current_section_id: str = ''
        current_section_group_prefix: str = ''
        for line_index in range(self.rules_start_line_index, len(loot_filter_lines)):
            line: str = loot_filter_lines[line_index]
            if (not in_rule):
                section_re_search_result = section_re_pattern.search(line)
                # Case: encountered new section or section group
                if (section_re_search_result):
                    is_section_group, section_id, section_name = \
                            self.ParseSectionDeclarationLine(line)
                    if (is_section_group):
                        current_section_group_prefix = '[' + section_name + '] '
                    else:
                        section_name = current_section_group_prefix + section_name
                    section_id = MakeUniqueId(section_id, self.section_map)
                    self.section_map[section_id] = section_name
                    self.inverse_section_map[section_name] = section_id
                    self.section_rule_map[section_id] = []
                    current_section_id = section_id
                # Case: encountered new rule
                elif (IsRuleStart(line)):
                    in_rule = True
                    current_rule_lines.append(line)
            else:  # in_rule
                if (line == ''):  # end of rule
                    rule_start_line_index: int = line_index - len(current_rule_lines)
                    new_rule = LootFilterRule(current_rule_lines, rule_start_line_index)
                    # Add rule to section rule map
                    self.section_rule_map[current_section_id].append(new_rule)
                    # Add rules to line index rule map
                    self.line_index_rule_map[rule_start_line_index] = new_rule
                    # Add rule to type tier rule map
                    if (new_rule.type not in self.type_tier_rule_map):
                        self.type_tier_rule_map[new_rule.type] = {}
                    if (new_rule.tier not in self.type_tier_rule_map[new_rule.type]):
                        self.type_tier_rule_map[new_rule.type][new_rule.tier] = []
                    self.type_tier_rule_map[new_rule.type][new_rule.tier].append(new_rule)
                    in_rule = False
                    current_rule_lines = []
                else:
                    current_rule_lines.append(line)
    # End ParseLootFitlerRules()
    
                
# -----------------------------------------------------------------------------

def RuleSearchExample(loot_filter: LootFilter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Find all sections matching keyword(s)
    keyword = 'currency'  # case insensitive
    matching_section_names: List[str] = loot_filter.SearchSectionNames(keyword)
    print('All sections matching keyword "', keyword, ':', sep='')
    print(' ->', '\n -> '.join(matching_section_names))
    print()
    
    # Find all rules of sections matching keyword search
    keyword = 'Regular Currency Tiering'
    matching_section_names: List[str] = loot_filter.SearchSectionNames(keyword)
    print('All rules matching keyword "', keyword, ':\n', sep='')
    for section_name in matching_section_names:
        section_rules: List[LootFilterRule] = loot_filter.GetSectionRules(section_name)
        print('### Section:', section_name, '###', '\n')
        for rule in section_rules:
            rule_start_line_number = rule.start_line_index + 1
            print('# Rule from line', rule_start_line_number, ' in loot filter:\n')
            print(rule)
            print('\n* * * * * * * * * * * * * * * * * * * *\n')
    
    # Find tier 1 currency rule
    section_name = 'Currency - Regular Currency Tiering'
    t1_currency_identifier = '$type->currency $tier->t1'
    section_rules: List[LootFilterRule] = loot_filter.GetSectionRules(section_name)
    print(type(section_rules))
    print(type(section_rules[0]))
    print('Searching for tier 1 currency rule...\n')
    for rule in section_rules:
        if (t1_currency_identifier in str(rule)):
            rule_start_line_number = rule.start_line_index + 1
            print('Found rule from line', rule_start_line_number, ' in loot filter:\n')
            print('type = "', rule.type, '", tier = "', rule.tier, '"\n', sep='')
            print(rule)
            print('\n* * * * * * * * * * * * * * * * * * * *\n')
            # Modify rule visibility and save filter to file
            rule.SetVisibility(RuleVisibility.kShow)
            rule.SetVisibility(RuleVisibility.kHide)
            rule.SetVisibility(RuleVisibility.kDisable)
    loot_filter.SaveToFile(kOutputLootFilterFilename)
    # Now just reload filter in-game and changes are applied
    
    # End RuleSearchExample()

def HideCurrencyTierExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Hide currency by tier:
    tier_number = 5
    print('Hiding T{} currency...\n'.format(tier_number))
    type_name = 'currency'
    tier_name = kCurrencyTierNames['t' + str(tier_number)]
    [found_currency_rule] = loot_filter.GetRulesByTypeTier(type_name, tier_name)
    print('Found rule:\n')
    print(found_currency_rule)
    found_currency_rule.SetVisibility(RuleVisibility.kHide)
    print('\nReplaced with rule:\n')
    print(found_currency_rule)
    print('\nSaving new filter to', kOutputLootFilterFilename)
    loot_filter.SaveToFile(kOutputLootFilterFilename)
    
def MoveCurrencyBetweenTiersExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Move Blessed Orbs down a tier
    base_type_name = 'Blessed Orb'
    starting_tier_number = 5
    target_tier_number = starting_tier_number + 1
    # Look up currency by tier
    type_name = 'currency'
    starting_tier_name = kCurrencyTierNames['t' + str(starting_tier_number)]
    [starting_currency_rule] = loot_filter.GetRulesByTypeTier(type_name, starting_tier_name)
    starting_currency_rule.RemoveBaseType(base_type_name)
    target_tier_name = kCurrencyTierNames['t' + str(target_tier_number)]
    [target_currency_rule] = loot_filter.GetRulesByTypeTier(type_name, target_tier_name)
    target_currency_rule.AddBaseType(base_type_name)
    print('Moved BaseType: {} from tier {} to tier {}\n'.format(
            base_type_name, starting_tier_number, target_tier_number))
    print(starting_currency_rule)
    print('\n* * * * * * * * * * * * * * * * * * * *\n')
    print(target_currency_rule)
    loot_filter.SaveToFile(kOutputLootFilterFilename)
    
def main():
    InitializeLog()
    loot_filter = LootFilter(kInputLootFilterFilename)
    MoveCurrencyBetweenTiersExample(loot_filter)
    

if (__name__ == '__main__'):
    main()
