import os.path
import re

from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Tuple

import config
import consts
import helper
import logger
import rule_parser
import test_consts
from type_checker import CheckType, CheckType2

# -----------------------------------------------------------------------------

class RuleVisibility(Enum):
    kShow = 1
    kHide = 2
    kDisable = 3  # rule is commented out
    kUnknown = 4
# End class RuleVisibility

# -----------------------------------------------------------------------------

class LootFilterRule:
    '''
    Member variables:
     - self.text_lines: List[str]
     - self.parsed_lines: list of (keyword, operator, values_list) triplets
     - self.has_continue: bool - indicates whether this rule has a "Continue" line
     - self.start_line_index: int - line index of this rule in the original filter file
     - self.visibility: RuleVisibility
     - self.type_tag: str - identifier found after "$type->" in the first line of the rule
     - self.tier_tag: str - identifier found after "$tier->" in the first line of the rule
     - self.base_type_list: List[str]
       - Note: not all rules must have BaseType, so base_type_list may be empty
     - self.base_type_line_index: int - index into self.text_lines (not full loot filter)
    '''

    def __init__(self, rule_text_lines: str or List[str], start_line_index: int):
        if (isinstance(rule_text_lines, str)):
            rule_text_lines = rule_text_lines.split('\n')
        # Now rule is a list of line strings
        CheckType(rule_text_lines, 'rule_text_lines', list)
        CheckType(start_line_index, 'start_line_index', int)
        if (len(rule_text_lines) == 0):
            logger.Log('Error: emtpy rule found starting on line {} of loot filter'.format(
                    start_line_index + 1))
        self.text_lines = rule_text_lines
        self.start_line_index = start_line_index  # index in full loot filter file
        # Generate self.parsed_lines and check for 'Continue' keyword
        self.parsed_lines = []
        self.has_continue = False
        for line in self.text_lines[1:]:
            self.parsed_lines.append(rule_parser.ParseRuleLineGeneric(line))
            if (helper.UncommentedLine(line).startswith('Continue')):
                self.has_continue = True
        self.parsed_lines = [rule_parser.ParseRuleLineGeneric(line) for line in self.text_lines[1:]]
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
        self.type_tag: str = first_line[type_start_index : type_end_index]
        self.tier_tag: str = first_line[tier_start_index : tier_end_index]
        # Parse base type list
        # Note - not all rules may have a base type, in which case base type list is empty
        # TODO: do we still need this?
        self.base_type_list = []
        self.base_type_line_index = -1
        for i in range(len(self.text_lines)):
            line: str = self.text_lines[i]
            if (line.startswith('BaseType') or line.startswith('#BaseType') or
                    line.startswith('# BaseType')):
                self.base_type_line_index = i
                self.base_type_list = helper.ParseBaseTypeLine(line)
        # TODO: parse size, color, etc...
    # End __init__
        
    def __repr__(self):
        return '\n'.join(self.text_lines)
    # End __repr__
    
    def MatchesItem(self, item_properties: dict) -> bool:
        return rule_parser.CheckRuleMatchesItem(self.parsed_lines, item_properties)
    # End MatchesItem
        
    def GetVisibility(self) -> RuleVisibility:
        return self.visibility
    # End GetVisibility
    
    def SetVisibility(self, visibility: RuleVisibility) -> None:
        CheckType(visibility, 'visibility', RuleVisibility)
        if (self.visibility == visibility): return
        # Case: Disable - comment all lines
        if (visibility == RuleVisibility.kDisable):
            self.text_lines = [helper.CommentedLine(line) for line in self.text_lines]
        # Case: Show - set first word to "Show" and uncomment all lines
        elif (visibility == RuleVisibility.kShow):
            self.text_lines = [helper.UncommentedLine(line) for line in self.text_lines]
            if (self.text_lines[0].startswith('Hide')):
                self.text_lines[0] = 'Show' + self.text_lines[0][4:]
        # Case: Hide - set first word to hide and comment effect lines
        elif (visibility == RuleVisibility.kHide):
            self.text_lines = [helper.UncommentedLine(line) for line in self.text_lines]
            if (self.text_lines[0].startswith('Show')):
                self.text_lines[0] = 'Hide' + self.text_lines[0][4:]
            #  Disable beams, minimap icons, and drop sounds
            kKeywordsToDisable = ['PlayEffect', 'MinimapIcon', 'PlayAlertSound']
            for parsed_lines_index in range(len(self.parsed_lines)):
                text_lines_index = parsed_lines_index + 1
                keyword, _, _ = self.parsed_lines[parsed_lines_index]
                if (keyword in kKeywordsToDisable):
                    self.text_lines[text_lines_index] = helper.CommentedLine(
                            self.text_lines[text_lines_index])
        # Update "Show" or "Hide" keyword in first line of rule
        #if ((visibility == RuleVisibility.kShow) and self.text_lines[0].startswith('Hide')):
        #    self.text_lines[0] = 'Show' + self.text_lines[0][4:]
        #elif ((visibility == RuleVisibility.kHide) and self.text_lines[0].startswith('Show')):
        #    self.text_lines[0] = 'Hide' + self.text_lines[0][4:]
        self.visibility = visibility
    # End SetVisibility
    
    # Note: BaseType names are *not* quoted in base_type_list
    def AddBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        if (base_type_name in self.base_type_list):
            return
        quoted_base_type_name = '"' + base_type_name + '"'
        self.base_type_list.append(base_type_name)
        self.text_lines[self.base_type_line_index] = \
                self.text_lines[self.base_type_line_index] + ' ' + quoted_base_type_name
    # End AddBaseType
    
    def RemoveBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        quoted_base_type_name = '"' + base_type_name + '"'
        if ((base_type_name not in self.base_type_list) and
                (quoted_base_type_name not in self.base_type_list)):
            logger.Log('Warning: requested to remove BaseType ' + base_type_name + ' from rule "' + 
                    self.text_lines[0] + '", but given BaseType is not in this rule')
            return
        self.base_type_list.remove(base_type_name)
        # Remove base_type_name from rule text
        index = self.base_type_line_index  # for convenience
        if (quoted_base_type_name in self.text_lines[self.base_type_line_index]):
            self.text_lines[index] = '{}BaseType {}'.format(
                    '# ' if self.visibility == RuleVisibility.kDisable else '',
                    '"' + '" "'.join(self.base_type_list) + '"')
        # Now if the BaseType line is empty, it will generate an error in PoE,
        # so we need to comment out the rule if no base types left
        if (len(self.base_type_list) == 0):
            self.SetVisibility(RuleVisibility.kDisable)
            # Also, need to eliminate the ' ""'  in the list
            self.text_lines[index] = self.text_lines[index][:-3]
    # End RemoveBaseType
    
    # Returns a bool indicating whether or not the line identified by the given keyword was found
    # Updates both parsed_item_lines and text_lines
    def ModifyLine(self, keyword: str, new_operator: str,
                   new_value_or_values: str or int or list[str]) -> bool:
        CheckType(keyword, 'keyword', str)
        CheckType(new_operator, 'new_operator', str)
        CheckType(new_value_or_values, 'new_value_or_values', (str, int, list))
        found_index: int = -1
        for i in range(len(self.parsed_lines)):
            if (self.parsed_lines[i][0] == keyword):
                found_index = i
                break
        if (found_index == -1):
            return False
        new_values_list = (new_value_or_values if isinstance(new_value_or_values, list)
                          else [str(new_value_or_values)])
        self.parsed_lines[found_index] = keyword, new_operator, new_values_list
        text_line: str = keyword
        if (new_operator != ''):
            text_line += ' ' + new_operator
        use_quotes: bool = any(' ' in value_string for value_string in new_values_list)
        text_line += ' ' + ('"' + '" "'.join(new_values_list) + '"' if use_quotes
                            else ' '.join(new_values_list))
        # The index in text_lines is 1 greater than in parsed_lines,
        # because parsed_lines excludes the first (Show/Hide) line
        self.text_lines[found_index + 1] = text_line
        return True
    # End ModifyLine
    
    def GetSize(self) -> int:
        pass
    # End GetSize
        
    def SetSize(self, size: int) -> None:
        pass
    # End SetSize
        
    def GetRuleTextLines(self) -> List[str]:
        return self.text_lines
    # End GetRuleTextLines
    
# End class LootFilterRule

# -----------------------------------------------------------------------------

class LootFilter:
    '''
    Member variables:
     - self.input_filter_fullpath
     - self.output_filter_fullpath
     - self.profile_fullpath
     - self.profile_fullpath
     - self.text_lines: List[str]
     - self.parser_index: int
     - self.section_map: OrderedDict[id: str, name: str]
     - self.inverse_section_map: Dict[name: str, id: str]
     - self.rules_start_line_index: int
     - self.section_rule_map: OrderedDict[section_name: str, List[LootFilterRule]]
     - self.rule_list: List[LootFilterRule] - in order of loot filter file
     - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
     - self.type_tier_rule_map: 2d dict - (type_tag, tier_tag) maps to a unique LootFilterRule
       Example: self.type_tier_rule_map['currency']['t1exalted']
    '''

    # ============================== Public API ==============================
    
    # Construct LootFilter object, parsing the given loot filter file
    def __init__(self, input_filter_fullpath: str,
                 output_filter_fullpath: str = config.kPathOfExileLootFilterFullpath,
                 profile_fullpath: str = config.kProfileFullpath):
        CheckType(input_filter_fullpath, 'input_filter_fullpath', str)
        CheckType(output_filter_fullpath, 'output_filter_fullpath', str)
        CheckType(profile_fullpath, 'profile_fullpath', str)
        self.input_filter_fullpath = input_filter_fullpath
        self.output_filter_fullpath = output_filter_fullpath
        self.profile_fullpath = profile_fullpath
        self.custom_rules_fullpath = profile_fullpath[: -len('.profile')] + '.rules'
        self.ParseInputFilterFile()
    # End __init__

    def SaveToFile(self):
        with open(self.output_filter_fullpath, 'w') as output_file:
            line_index: int = 0
            while (line_index < len(self.text_lines)):
                line: str = self.text_lines[line_index]
                # If not a new rule start, just write input line back out
                if (not helper.IsRuleStart(self.text_lines, line_index)):
                    output_file.write(line + '\n')
                    line_index += 1
                # Otherwise is a new rule - write out the rule from line_index_rule_map
                else:  # IsRuleStart
                    rule = self.line_index_rule_map[line_index]
                    output_file.write(str(rule) + '\n')
                    line_index += len(rule.text_lines)
    # End SaveToFile
    
    # In NeverSink's fitler, type_tags plus tier_tags form a unique key for rules,
    # *except* for rules that have no type or tier tags.
    # When parsing, we create unique tags for rules missing tags, to create a unique key.
    def GetRuleByTypeTier(self, type_tag: str, tier_tag: str) -> LootFilterRule:
        CheckType(type_tag, 'type_tag', str)
        CheckType(tier_tag, 'tier_tag', str)
        return self.type_tier_rule_map[type_tag][tier_tag]
    # End GetRulesByTypeTier
    
    # ============================= Rule-Item Matching =============================
    
    # Finds the first rule in the filter matching the given item
    # Returns type_tag, tier_tag to uniquely identify the matched rule
    # Returns None, None if no rule matched
    # Cannot match AreaLevel restrictions:
    #  - if a rule has an AreaLevel requirement, it will never match any item
    def GetRuleMatchingItem(self, item_text_lines: List[str]) -> Tuple[str, str]:
        CheckType2(item_text_lines, 'item_text_lines', list, str)
        item_properties: dict = rule_parser.ParseItem(item_text_lines)
        #print('\nitem_properties:')
        #for k, v in item_properties.items():
        #    print(k, ':', v)
        #print()
        matched_continue_rule = None
        for rule in self.rule_list:
            if ((rule.visibility != RuleVisibility.kDisable) and rule.MatchesItem(item_properties)):
                #print('Matched rule:')
                #print('\n'.join(rule.text_lines))
                #print()
                if (rule.has_continue):
                    matched_continue_rule = rule
                else:
                    return rule.type_tag, rule.tier_tag
        if (matched_continue_rule):
            return matched_continue_rule.type_tag, matched_continue_rule.tier_tag
        return None, None
    # End GetRuleMatchingItem
    
    def SetRuleVisibility(self, type_tag: str, tier_tag: str, visibility: RuleVisibility) -> bool:
        CheckType(type_tag, 'type_tag', str)
        CheckType(tier_tag, 'tier_tag', str)
        CheckType(visibility, 'visibility', RuleVisibility)
        try:
            rule = self.type_tier_rule_map[type_tag][tier_tag]
        except KeyError:
            return False
        else:
            rule.SetVisibility(visibility)
            return True
    # End SetRuleVisibility
    
    # ========================= Section-Related Functions =========================
       
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
    
    # =========================== Map-Related Functions ===========================
    
    def SetHideMapsBelowTierTier(self, tier: int) -> int:
        CheckType(tier, 'tier', int)
        type_name = 'dlf_hide_maps_below_tier'
        tier_name = type_name
        rule = self.type_tier_rule_map[type_name][tier_name]
        for i in range(len(rule.text_lines)):
            line = rule.text_lines[i]
            keystring: str = 'MapTier < '
            if (keystring in line):
                maptier_start_index = line.find(keystring) + len(keystring)
                rule.text_lines[i] = line[:maptier_start_index] + str(tier)
                break
    # End SetHideMapsBelowTierTier
    
    def GetHideMapsBelowTierTier(self) -> int:
        type_name = 'dlf_hide_maps_below_tier'
        tier_name = type_name
        rule = self.type_tier_rule_map[type_name][tier_name]
        for line in rule.text_lines:
            keystring: str = 'MapTier < '
            if (keystring in line):
                maptier_start_index = line.find(keystring) + len(keystring)
                return helper.ParseNumberFromString(line, maptier_start_index)
    # End GetHideMapsBelowTierTier
    
    # =========================== Flask-Related Functions ==========================
    
    def SetFlaskRuleEnabledFor(self, flask_base_type: str, enable_flag: bool):
        CheckType(flask_base_type, 'flask_base_type', str)
        CheckType(enable_flag, 'enable_flag', bool)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        if (enable_flag):
            rule.AddBaseType(flask_base_type)
            # Rule may have been disabled if BaseType line was previously empty
            rule.SetVisibility(RuleVisibility.kShow)
        else:  # disable
            rule.RemoveBaseType(flask_base_type)
    # End SetFlaskRuleEnabledFor
    
    def IsFlaskRuleEnabledFor(self, flask_base_type: str) -> bool:
        CheckType(flask_base_type, 'flask_base_type', str)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        if (rule.visibility != RuleVisibility.kShow):
            return False
        return flask_base_type in rule.base_type_list
    # End IsFlaskRuleEnabledFor
    
    def GetAllEnabledFlaskTypes(self) -> List[str]:
        type_tag = 'dlf_flasks'
        tier_tag = type_tag
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        if (rule.visibility != RuleVisibility.kShow):
            return []
        return rule.base_type_list
    
    # ========================= Currency-Related Functions =========================
        
    def SetCurrencyToTier(self, currency_name: str, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(target_tier, 'target_tier', int)
        original_tier: int = self.GetTierOfCurrency(currency_name)
        self.MoveCurrencyFromTierToTier(currency_name, original_tier, target_tier)
    # End MoveCurrencyToTier
    
    def AdjustTierOfCurrency(self, currency_name: str, tier_delta: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(tier_delta, 'tier_delta', int)
        original_tier: int = self.GetTierOfCurrency(currency_name)
        target_tier: int = original_tier + tier_delta
        self.MoveCurrencyFromTierToTier(currency_name, original_tier, target_tier)
    # End AdjustTierOfCurrency
    
    def GetAllCurrencyInTier(self, tier: int) -> List[str]:
        CheckType(tier, 'tier', int)
        if (tier not in consts.kCurrencyTierNames):
            logger.Log('Warning: currency tier {} is outside the valid currency tier range [0, 9]'
                        .format(tier))
            return []
        type_tag = consts.kCurrencyTypeTag
        tier_tag = consts.kCurrencyTierNames[tier]
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        return rule.base_type_list
    # End GetAllCurrencyInTier
    
    # Returns the name of the tier to which the given currency belongs
    def GetTierOfCurrency(self, currency_name: str) -> int:
        CheckType(currency_name, 'currency_name', str)
        type_tag = consts.kCurrencyTypeTag
        for tier_tag in consts.kCurrencyTierNames.values():
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            if (currency_name in rule.base_type_list):
                return consts.kCurrencyTierNameToNumberMap[tier_tag]
        logger.Log('Warning: currency "{}" not found in normal currency tiers'.format(
                           currency_name))
        return -1
    # End GetTierOfCurrency
        
    def MoveCurrencyFromTierToTier(self, currency_name: str, original_tier: int, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(original_tier, 'original_tier', int)
        CheckType(target_tier, 'target_tier', int)
        if (not (1 <= target_tier <= 9)):
            logger.Log(('Warning: currency "{}" could not be moved from tier {} to tier {}, '
                        'target tier is out of the valid currency tier range: [1, 9]').format(
                                currency_name, original_tier, target_tier))
            return
        type_tag = consts.kCurrencyTypeTag
        # Remove currency_name from original_tier rule
        original_tier_tag = consts.kCurrencyTierNames[original_tier]
        original_rule = self.type_tier_rule_map[type_tag][original_tier_tag]
        original_rule.RemoveBaseType(currency_name)
        # Add currency_name to target_tier rule
        target_tier_tag = consts.kCurrencyTierNames[target_tier]
        target_currency_rule = self.type_tier_rule_map[type_tag][target_tier_tag]
        target_currency_rule.AddBaseType(currency_name)
    # End MoveCurrencyFromTierToTier
    
    def SetCurrencyTierVisibility(self, tier: int or str, visibility: RuleVisibility):
        CheckType(tier, 'tier', (int, str))
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag = consts.kCurrencyTypeTag
        tier_tag = consts.kCurrencyTierNames[tier] if isinstance(tier, int) else tier
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        rule.SetVisibility(visibility)
    # SetCurrencyTierVisibility
    
    def GetCurrencyTierVisibility(self, tier: int or str) -> RuleVisibility:
        CheckType(tier, 'tier', (int, str))
        type_tag = consts.kCurrencyTypeTag
        tier_tag = consts.kCurrencyTierNames[tier] if isinstance(tier, int) else tier
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        return rule.visibility
    # GetCurrencyTierVisibility
    
    def SetHideCurrencyAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kMaxCurrencyTier):
            visibility = RuleVisibility.kHide if tier > max_visible_tier else RuleVisibility.kShow
            self.SetCurrencyTierVisibility(tier, visibility)
    # SetHideCurrencyAboveTierTier
    
    def GetHideCurrencyAboveTierTier(self) -> int:
        max_visible_tier: int = 0
        for tier in range(1, consts.kMaxCurrencyTier):
            if (self.GetCurrencyTierVisibility(tier) == RuleVisibility.kShow):
                max_visible_tier = tier
            else:
                break
        return max_visible_tier
    # GetHideCurrencyAboveTierTier
    
    # =========================== Unique Item Functions ===========================
    
    def SetUniqueTierVisibility(self, tier: int or str, visibility: RuleVisibility):
        CheckType(tier, 'tier', (int, str))
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag = consts.kUniqueTypeTag
        tier_tag = consts.kUniqueTierNames[tier] if isinstance(tier, int) else tier
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        rule.SetVisibility(visibility)
    # SetUniqueTierVisibility
    
    def GetUniqueTierVisibility(self, tier: int or str) -> RuleVisibility:
        CheckType(tier, 'tier', (int, str))
        type_tag = consts.kUniqueTypeTag
        tier_tag = consts.kUniqueTierNames[tier] if isinstance(tier, int) else tier
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        return rule.visibility
    # GetUniqueTierVisibility
    
    def SetHideUniquesAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kMaxUniqueTier):
            visibility = RuleVisibility.kHide if tier > max_visible_tier else RuleVisibility.kShow
            self.SetUniqueTierVisibility(tier, visibility)
    # SetHideUniquesAboveTierTier
    
    def GetHideUniquesAboveTierTier(self) -> int:
        max_visible_tier: int = 0
        for tier in range(1, consts.kMaxUniqueTier):
            if (self.GetUniqueTierVisibility(tier) == RuleVisibility.kShow):
                max_visible_tier = tier
            else:
                break
        return max_visible_tier
    # GetHideUniquesAboveTierTier
    
    # ============================ Gem Quality Functions ============================
    
    # The rules we modify for gem-quality functionality are:
    #  - Show # %D5 $type->gems-generic $tier->qt2   (19-20)
    #  - Show # %D3 $type->gems-generic $tier->qt3   (14-18)
    #  - Show # %D2 $type->gems-generic $tier->qt4   (1-13)
    def SetGemMinQuality(self, min_quality: int):
        type_tag: str = 'gems-generic'
        tier_tag_base: str = 'qt'
        quality_t2_rule = self.type_tier_rule_map[type_tag][tier_tag_base + str(2)]
        quality_t3_rule = self.type_tier_rule_map[type_tag][tier_tag_base + str(3)]
        quality_t4_rule = self.type_tier_rule_map[type_tag][tier_tag_base + str(4)]
        if (19 <= min_quality <= 20):
            quality_t2_rule.SetVisibility(RuleVisibility.kShow)
            quality_t2_rule.ModifyLine('Quality', '>=', min_quality)
            quality_t3_rule.SetVisibility(RuleVisibility.kDisable)
            quality_t4_rule.SetVisibility(RuleVisibility.kDisable)
        elif (14 <= min_quality <= 18):
            quality_t2_rule.SetVisibility(RuleVisibility.kShow)
            quality_t2_rule.ModifyLine('Quality', '>=', 19)
            quality_t3_rule.SetVisibility(RuleVisibility.kShow)
            quality_t3_rule.ModifyLine('Quality', '>=', min_quality)
            quality_t4_rule.SetVisibility(RuleVisibility.kDisable)
        elif (1 <= min_quality <= 13):
            quality_t2_rule.SetVisibility(RuleVisibility.kShow)
            quality_t2_rule.ModifyLine('Quality', '>=', 19)
            quality_t3_rule.SetVisibility(RuleVisibility.kShow)
            quality_t3_rule.ModifyLine('Quality', '>=', 14)
            quality_t4_rule.SetVisibility(RuleVisibility.kShow)
            quality_t4_rule.ModifyLine('Quality', '>=', min_quality)
    # End SetGemMinQuality
    
    def GetGemMinQuality(self):
        type_tag: str = 'gems-generic'
        tier_tag_base: str = 'qt'
        for tier in [4, 3, 2, 1]:
            rule = self.type_tier_rule_map[type_tag][tier_tag_base + str(tier)]
            if (rule.visibility == RuleVisibility.kShow):
                for keyword, operator, value_string_list in rule.parsed_lines:
                    if keyword == 'Quality':
                        return int(value_string_list[0])
        return -1  # indicates all gem quality rules are disabled/hidden
    
    # ======================= Chaos Recipe-Related Functions =======================
    
    def SetChaosRecipeEnabledFor(self, item_slot: str, enable_flag: bool):
        CheckType(item_slot, 'item_slot', str)
        CheckType(enable_flag, 'enable_flag', bool)
        if ((item_slot == 'Weapons') or (item_slot == 'weapons')):
            self.SetChaosRecipeEnabledFor('WeaponsX', enable_flag)
            self.SetChaosRecipeEnabledFor('Weapons3', enable_flag)
            return
        type_tag: str = 'dlf_chaos_recipe_rares'
        tier_tag: str = (item_slot if item_slot in consts.kChaosRecipeTierTags.values()
                         else consts.kChaosRecipeTierTags[item_slot])
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        rule.SetVisibility(RuleVisibility.kShow if enable_flag else RuleVisibility.kDisable)
    # End IsChaosRecipeItemSlotEnabled
    
    def IsChaosRecipeEnabledFor(self, item_slot: str) -> bool:
        CheckType(item_slot, 'item_slot', str)
        if ((item_slot == 'Weapons') or (item_slot == 'weapons')):
            return self.IsChaosRecipeEnabledFor('WeaponsX')
        type_tag: str = 'dlf_chaos_recipe_rares'
        tier_tag: str = (item_slot if item_slot in consts.kChaosRecipeTierTags.values()
                         else consts.kChaosRecipeTierTags[item_slot])
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        return rule.visibility == RuleVisibility.kShow
    # End IsChaosRecipeItemSlotEnabled
    
    # ======================== Private Parser Methods ========================
    
    def ParseInputFilterFile(self) -> None:
        # Read in lines from file   
        self.text_lines: List[str] = []
        with open(self.input_filter_fullpath) as input_filter_file:
            for line in input_filter_file:
                self.text_lines.append(line.strip())
        # Ensure there is a blank line at the end to make parsing algorithms cleaner
        if (self.text_lines[-1] != ''):
            self.text_lines.append('')
        self.rules_start_line_index = self.FindRulesStartLineIndex()
        self.parser_index = self.rules_start_line_index
        # Add custom user-defiend rulies plus DLF-generated rules like chaos recipe rules
        self.AddDlfRulesIfMissing()
        self.ParseLootFilterRules()
    # End ParseLootFilterFile()
    
    def FindRulesStartLineIndex(self) -> int:
        found_table_of_contents: bool = False
        for line_index in range(len(self.text_lines)):
            line: str = self.text_lines[line_index]
            if (consts.kTableOfContentsIdentifier in line):
                found_table_of_contents = True
            elif(not found_table_of_contents):
                continue
            # Blank line indicates end of table of contents
            elif (line == ''):
                return line_index + 1
        return -1  # never found table of contents
    # End FindRulesStartLineIndex
    
    def AddDlfRulesIfMissing(self):
        index = self.rules_start_line_index
        for index in range(self.rules_start_line_index, len(self.text_lines)):
            line: str = self.text_lines[index]
            if (helper.IsSectionOrGroupDeclaration(line)):
                _, section_id, section_name = helper.ParseSectionDeclarationLine(line)
                if (section_id == consts.kDlfAddedRulesSectionGroupId
                        and section_name == consts.kDlfAddedRulesSectionGroupName):
                    # found DLF rules, so we can just return
                    return
                break  # as soon as we encounter any section declaration, we're done
        # Add DLF rules
        to_add_string_list: List[str] = []
        # Add section group header
        to_add_string: str = consts.kSectionGroupHeaderTemplate.format(
                consts.kDlfAddedRulesSectionGroupId,
                consts.kDlfAddedRulesSectionGroupName)
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        current_section_id_int: int = int(consts.kDlfAddedRulesSectionGroupId)
        # Add custom user-defined rules
        if (os.path.isfile(self.custom_rules_fullpath)):
            current_section_id_int += 1
            custom_rules_filename: str = os.path.basename(self.custom_rules_fullpath)
            to_add_string = consts.kSectionHeaderTemplate.format(
                    current_section_id_int, 'Custom rules from ' + custom_rules_filename)
            to_add_string_list.extend(to_add_string.split('\n') + [''])
            with open(self.custom_rules_fullpath) as custom_rules_file:
                custom_rules_lines: List[str] = custom_rules_file.readlines()
            custom_rules_lines = [line.strip() for line in custom_rules_lines]
            custom_rules_lines.append('')  # append blank line to handle end uniformly
            current_rule_lines: List[str] = []
            custom_rule_count: int = 0
            for line_index in range(len(custom_rules_lines)):
                line: str = custom_rules_lines[line_index]
                if (line == ''):
                    if (len(current_rule_lines) == 0):
                        continue
                    else:
                        # End of rule -> add rule, reset lines, and increment count
                        to_add_string_list.extend(current_rule_lines + [''])
                        current_rule_lines = []
                        custom_rule_count += 1
                elif (helper.IsRuleStart(custom_rules_lines, line_index)):
                    type_tag = 'custom_rule'
                    tier_tag = str(custom_rule_count)
                    current_rule_lines.append(
                            line + ' # $type->{} $tier->{}'.format(type_tag, tier_tag))
                else:  # nonempty line
                    current_rule_lines.append(line)
        # Add "Hide maps below tier" rule
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Hide all maps below specified tier')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        to_add_string = consts.kHideMapsBelowTierRuleTemplate.format(
                config.kHideMapsBelowTier)
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Add flask rule
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Show specific flask BaseTypes')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        to_add_string = consts.kFlaskRuleTemplate
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Add chaos recipe rules
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Chaos recipe rares')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        for chaos_recipe_rule_string in consts.kChaosRecipeRuleStrings:
            to_add_string_list.extend(chaos_recipe_rule_string.split('\n') + [''])
        # Update self.text_lines to contain the newly added rules
        # Python trick to insert one list into another: https://stackoverflow.com/a/5805910
        insert_index: int = self.rules_start_line_index
        self.text_lines[insert_index : insert_index] = to_add_string_list
    # End AddDlfRulesIfMissing
    
    def ParseLootFilterRules(self) -> None:
        '''
        This function parses the rules of the loot filter into the following data structures:
         - self.section_map: OrderedDict[id: str, name: str]
         - self.inverse_section_map: Dict[name: str, id: str]
         - self.rules_start_line_index: int
         - self.section_rule_map: OrderedDict[section_name: str, List[LootFilterRule]]
         - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
         - self.rule_list: List[LootFilterRule]
         - self.type_tier_rule_map: 2d dict - (type_tag, tier_tag) maps to a unique LootFilterRule
           Note: parser ensures that (type_tag, tier_tag) forms a unique key for rules
           Example: self.type_tier_rule_map['currency']['t1'] 
        '''
        # Initialize data structures to store parsed data
        self.section_map: OrderedDict[str, str] = {}  # maps ids to names
        self.inverse_section_map: Dict[str, str] = {}  # maps names to ids
        self.section_rule_map: OrderedDict[str, List[LootFilterRule]] = OrderedDict()
        self.line_index_rule_map: OrderedDict[int, LootFilterRule] = OrderedDict()
        self.rule_list: List[LootFilterRule] = []
        self.type_tier_rule_map = {}
        # Set up parsing loop
        in_rule: bool = False
        current_rule_lines: List[str] = []
        current_section_id: str = ''
        current_section_group_prefix: str = ''
        untagged_rule_count: int = 0
        for line_index in range(self.rules_start_line_index, len(self.text_lines)):
            line: str = self.text_lines[line_index]
            if (not in_rule):
                # Case: encountered new section or section group
                if (helper.IsSectionOrGroupDeclaration(line)):
                    is_section_group, section_id, section_name = \
                            helper.ParseSectionDeclarationLine(line)
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
                elif (helper.IsRuleStart(self.text_lines, line_index)):
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
                    # Generate unique type-tier tag pair if no tags
                    # (For now we assume it either has both or none)
                    if ((new_rule.type_tag == '') and (new_rule.tier_tag == '')):
                        new_rule.type_tag = 'untagged_rule'
                        new_rule.tier_tag = str(untagged_rule_count)
                        untagged_rule_count += 1
                        current_rule_lines[0] += ' # ' + consts.kTypeTierTagTemplate.format(
                                new_rule.type_tag, new_rule.tier_tag)
                    # Add rule to rule list
                    self.rule_list.append(new_rule)
                    # Add rule to type tier rule map
                    if (new_rule.type_tag not in self.type_tier_rule_map):
                        self.type_tier_rule_map[new_rule.type_tag] = {}
                    self.type_tier_rule_map[new_rule.type_tag][new_rule.tier_tag] = new_rule
                    in_rule = False
                    current_rule_lines = []
                else:
                    current_rule_lines.append(line)
    # End ParseLootFilterRules()

# -----------------------------------------------------------------------------
