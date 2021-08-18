import re

from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Tuple

import consts
import helper
import logger
from type_checker import CheckType

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

    def __init__(self, rule_text_lines: str or List[str], start_line_index: int):
        if (isinstance(rule_text_lines, str)):
            rule_text_lines = rule_text_lines.split('\n')
        CheckType(rule_text_lines, 'rule_text_lines', list)
        CheckType(start_line_index, 'start_line_index', int)
        if (len(rule_text_lines) == 0):
            logger.Log('Error: emtpy rule found starting on line {} of loot filter'.format(
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
            logger.Log(('Warning: unable to determine rule visibility for rule starting on line {}'
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
                self.base_type_list = helper.ParseBaseTypeLine(line)
        # TODO: parse size, color, etc...
    # End __init__()
        
    def __repr__(self):
        return '\n'.join(self.text_lines)
    # End __repr__()
        
    def GetVisibility(self) -> RuleVisibility:
        return self.visibility
    # End GetVisibility()
    
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
            comment_prefix_length = helper.FindFirstMatchingPredicate(
                    self.text_lines[0], str.isalnum)
            for i in range(len(self.text_lines)):
                self.text_lines[i] = self.text_lines[i][comment_prefix_length :]
        # Toggle Show/Hide
        if ((visibility == RuleVisibility.kShow) and self.text_lines[0].startswith('Hide')):
            self.text_lines[0] = 'Show' + self.text_lines[0][4:]
        elif ((visibility == RuleVisibility.kHide) and self.text_lines[0].startswith('Show')):
            self.text_lines[0] = 'Hide' + self.text_lines[0][4:]
        self.visibility = visibility
    # End SetVisibility
    
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
            logger.Log('Warning: requested to remove BaseType ' + base_type_name + ' from rule "' + 
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
    # End GetSize()
        
    def SetSize(self, size: int) -> None:
        pass
    # End SetSize()
        
    def GetRuleTextLines(self) -> List[str]:
        return self.text_lines
    # End GetRuleTextLines()

# -----------------------------------------------------------------------------

class LootFilter:
    '''
    Member variables:
     - self.text_lines: List[str]
     - self.section_map: OrderedDict[id: str, name: str]
     - self.inverse_section_map: Dict[name: str, id: str]
     - self.rules_start_line_index: int
     - self.section_rule_map: OrderedDict[section_name: str, List[LootFilterRule]]
     - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
     - self.type_tier_rule_map: 2d dict which allows you to access rules by type and tier
       Example: self.type_tier_rule_map['currency']['t1exalted']  
                    -> list of rules of type 'currency' and tier 't1'
    '''

    # ============================== Public API ==============================
    
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
                if (not helper.IsRuleStart(line)):
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
    # End GetRulesByTypeTier
       
    def ContainsSection(self, section_name: str) -> bool:
        CheckType(section_name, 'section_name', str)
        return section_name in self.inverse_section_map
    # End ContainsSection
    
    def ContainsSectionId(self, section_id: str) -> bool:
        CheckType(section_id, 'section_id', str)
        return section_id in self.section_map
    # End ContainsSectionId
    
    def GetSectionId(self, section_name: str) -> str:
        CheckType(section_name, 'section_name', str)
        return self.inverse_section_map[section_name]
    # End GetSectionId
    
    def GetSectionName(self, section_id: str) -> str:
        CheckType(section_id, 'section_id', str)
        return self.section_map[section_id]
    # End GetSectionName

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
    # End SearchSectionNames
    
    def GetSectionRules(self, section_name: str) -> List[LootFilterRule]:
        CheckType(section_name, 'section_name', str)
        section_id: str = self.inverse_section_map[section_name]
        return self.section_rule_map[section_id]
    # End GetSectionRules
    
    def ChangeRuleVisibility(self, section_name: str, rule_index: int,
                             visibility: RuleVisibility) -> None:
        CheckType(section_name, 'section_name', str)
        CheckType(rule_index, 'rule_index', int)
        self.GetSectionRules(section_name)[rule_index].SetVisibility(visibility)
    # End ChangeRuleVisibility
    
    def GetAllCurrencyInTier(self, tier: int) -> List[str]:
        CheckType(tier, 'tier', int)
        if (tier not in consts.kCurrencyTierNames):
            logger.Log('Warning: currency tier {} is outside the valid currency tier range [0, 9]'
                        .format(tier))
            return []
        type_name = 'currency'
        tier_name = consts.kCurrencyTierNames[tier]
        [rule] = self.type_tier_rule_map[type_name][tier_name]
        return rule.base_type_list
    # End GetAllCurrencyInTier
    
    # Returns the name of the tier to which the given currency belongs
    def GetTierOfCurrency(self, currency_name: str) -> int:
        CheckType(currency_name, 'currency_name', str)
        type_name = 'currency'
        for tier_name in consts.kCurrencyTierNames.values():
            [rule] = self.type_tier_rule_map[type_name][tier_name]
            if (currency_name in rule.base_type_list):
                return consts.kCurrencyTierNameToNumberMap[tier_name]
        logger.Log('Warning: currency "{}" not found in normal currency tiers'.format(
                           currency_name))
        return -1
    # End GetTierOfCurrency
    
    def AdjustTierOfCurrency(self, currency_name: str, tier_delta: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(tier_delta, 'tier_delta', int)
        original_tier: int = self.GetTierOfCurrency(currency_name)
        target_tier: int = original_tier + tier_delta
        self.MoveCurrencyFromTierToTier(currency_name, original_tier, target_tier)
    # End AdjustTierOfCurrency
        
    def SetCurrencyToTier(self, currency_name: str, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(target_tier, 'target_tier', int)
        original_tier: int = self.GetTierOfCurrency(currency_name)
        self.MoveCurrencyFromTierToTier(currency_name, original_tier, target_tier)
    # End MoveCurrencyToTier
        
    def MoveCurrencyFromTierToTier(self, currency_name: str, original_tier: int, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(original_tier, 'original_tier', int)
        CheckType(target_tier, 'target_tier', int)
        if (not (1 <= target_tier <= 9)):
            logger.Log(('Warning: currency "{}" could not be moved from tier {} to tier {}, '
                        'target tier is out of the valid currency tier range: [1, 9]').format(
                                currency_name, original_tier, target_tier))
            return
        type_name = 'currency'
        # Remove currency_name from original_tier rule
        original_tier_name = consts.kCurrencyTierNames[original_tier]
        [original_rule] = self.type_tier_rule_map[type_name][original_tier_name]
        original_rule.RemoveBaseType(currency_name)
        # Add currency_name to target_tier rule
        target_tier_name = consts.kCurrencyTierNames[target_tier]
        [target_currency_rule] = self.type_tier_rule_map[type_name][target_tier_name]
        target_currency_rule.AddBaseType(currency_name)
    # End MoveCurrencyFromTierToTier
    
    # ======================== Private Helper Methods ========================
    
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
    
    def FindRulesStartLineIndex(self, loot_filter_lines: List[str]) -> int:
        CheckType(loot_filter_lines, 'loot_filter_lines', list)
        found_table_of_contents: bool = False
        for line_index in range(len(loot_filter_lines)):
            line: str = loot_filter_lines[line_index]
            if (consts.kTableOfContentsIdentifier in line):
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
         - self.section_rule_map: OrderedDict[section_name: str, List[LootFilterRule]]
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
        self.rules_start_line_index: int = self.FindRulesStartLineIndex(loot_filter_lines)
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
                    section_id = helper.MakeUniqueId(section_id, self.section_map)
                    self.section_map[section_id] = section_name
                    self.inverse_section_map[section_name] = section_id
                    self.section_rule_map[section_id] = []
                    current_section_id = section_id
                # Case: encountered new rule
                elif (helper.IsRuleStart(line)):
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
    # End ParseLootFilterRules()

# -----------------------------------------------------------------------------
