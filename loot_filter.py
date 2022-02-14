import os.path
import re
import itertools

from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Tuple

import consts
import helper
import logger
import profile
import rule_parser
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
     - self.show_flag: bool - true for Show, false for Hide
     - self.type_tag: str - identifier found after "$type->" in the first line of the rule
     - self.tier_tag: str - identifier found after "$tier->" in the first line of the rule
     - self.base_type_list: List[str]
       - Note: not all rules must have BaseType, so base_type_list may be empty
     - self.base_type_line_index: int - index into self.text_lines (not full loot filter)
     - self.archnemesis_mod_list: List[str]
     - self.archnemesis_mod_line_index: int
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
        # Find the line index containing Show/Hide/Disable and save as self.tag_line_index
        self.tag_line_index = helper.FindTagLineIndex(self.text_lines)
        if (self.tag_line_index == -1):
            raise RuntimeError('did not find Show/Hide/Disable line in rule:\n{}'.format(
                    self.text_lines))
        # Generate self.parsed_lines and check for 'Continue' keyword
        self.parsed_lines = []
        self.has_continue = False
        for line in self.text_lines[1:]:
            self.parsed_lines.append(rule_parser.ParseRuleLineGeneric(line))
            if (helper.UncommentedLine(line).startswith('Continue')):
                self.has_continue = True
        self.parsed_lines = [rule_parser.ParseRuleLineGeneric(line) for line in self.text_lines[1:]]
        # Parse rule visibility
        self.show_flag = helper.ParseShowFlag(rule_text_lines)
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
        self.base_type_list = []
        self.base_type_line_index = -1
        for i in range(len(self.text_lines)):
            line: str = self.text_lines[i]
            if (line.startswith('BaseType') or line.startswith('#BaseType') or
                    line.startswith('# BaseType')):
                self.base_type_line_index = i
                self.base_type_list = helper.ParseBaseTypeLine(line)
        # Parse archnemesis mod list
        # Note - not all rules may have a base type, in which case base type list is empty
        self.archnemesis_mod_list = []
        self.archnemesis_mod_line_index = -1
        for i in range(len(self.text_lines)):
            line: str = self.text_lines[i]
            if (line.startswith('ArchnemesisMod') or line.startswith('#ArchnemesisMod') or
                    line.startswith('# ArchnemesisMod')):
                self.archnemesis_mod_line_index = i
                self.archnemesis_mod_list = helper.ParseArchnemesisModLine(line)
        # TODO: parse size, color, etc...
    # End __init__
        
    def __repr__(self):
        return '\n'.join(self.text_lines)
    # End __repr__
    
    # Adds type and tier tags to the Show/Hide/Disable line, and updates
    # self.type_tag and self.tier_tag accordingly
    def AddTypeTierTags(self, type_tag: str, tier_tag: str):
        self.type_tag = type_tag
        self.tier_tag = tier_tag
        self.text_lines[self.tag_line_index] += ' # ' + consts.kTypeTierTagTemplate.format(
                type_tag, tier_tag)
    # End AddTypeTierTags
    
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
            if (not self.show_flag):
                self.text_lines[0] = 'Show' + self.text_lines[0][4:]
            self.show_flag = True
        # Case: Hide - set first word to hide and comment effect lines
        elif (visibility == RuleVisibility.kHide):
            self.text_lines = [helper.UncommentedLine(line) for line in self.text_lines]
            if (self.show_flag):
                self.text_lines[0] = 'Hide' + self.text_lines[0][4:]
            self.show_flag = False
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
    
    # Uncomments the rule if it was commented before
    def Enable(self) -> None:
        if (self.visibility == RuleVisibility.kDisable):
            self.text_lines = [helper.UncommentedLine(line) for line in self.text_lines]
            self.visibility = RuleVisibility.kShow if self.show_flag else RuleVisibility.kHide
    # End Enable
        
    # Adds base_type_name to this rule's BaseType line, if it's not there already
    # Note: BaseType names are *not* quoted in base_type_list
    # TODO: If we add a basetype to a rule that was disabled (because its basetype line
    # was previously emptied), do we re-enable the rule properly?
    def AddBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        if (base_type_name in self.base_type_list):
            return
        # Check if rule is missing BaseType line, and add if so
        if (self.base_type_line_index == -1):
            base_type_line = "BaseType"
            if (self.visibility == RuleVisibility.kDisable):
                base_type_line = '# ' + base_type_line
            self.base_type_line_index = len(self.text_lines)
            self.text_lines.append(base_type_line)
        quoted_base_type_name = '"' + base_type_name + '"'
        self.base_type_list.append(base_type_name)
        self.text_lines[self.base_type_line_index] += ' ' + quoted_base_type_name
    # End AddBaseType
    
    # Removes base_type_name from this rule's BaseType line, if it's there
    def RemoveBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        quoted_base_type_name = '"' + base_type_name + '"'
        # TODO: potential bug here, this checks two things, removal could fail after
        if ((base_type_name not in self.base_type_list) and
                (quoted_base_type_name not in self.base_type_list)):
            return
        self.base_type_list.remove(base_type_name)
        # Remove base_type_name from rule text
        index = self.base_type_line_index  # for convenience
        if (quoted_base_type_name in self.text_lines[index]):
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
    
    def ClearBaseTypeList(self):
        while (len(self.base_type_list) > 0):
            self.RemoveBaseType(self.base_type_list[-1])
    # End ClearBaseTypeList
        
    # ArchnemesisModList functions: analogous to BaseType functions above
    # Adds archnemesis_mod_name to the rule's ArchnemesisMod line (if not there already)
    def AddArchnemesisMod(self, archnemesis_mod_name: str):
        CheckType(archnemesis_mod_name, 'archnemesis_mod_name', str)
        if (archnemesis_mod_name in self.archnemesis_mod_list):
            return
        # Check if rule is missing ArchnemesisMod line, and add if so
        if (self.archnemesis_mod_line_index == -1):
            archnemesis_mod_line = "ArchnemesisMod"
            if (self.visibility == RuleVisibility.kDisable):
                archnemesis_mod_line = '# ' + archnemesis_mod_line
            self.archnemesis_mod_line_index = len(self.text_lines)
            self.text_lines.append(archnemesis_mod_line)
        quoted_archnemesis_mod_name = '"' + archnemesis_mod_name + '"'
        self.archnemesis_mod_list.append(archnemesis_mod_name)
        self.text_lines[self.archnemesis_mod_line_index] += ' ' + quoted_archnemesis_mod_name
    # End AddArchnemesisMod
    
    # Removes archnemesis_mod_name from this rule's ArchnemesisMod line, if it's there
    def RemoveArchnemesisMod(self, archnemesis_mod_name: str):
        CheckType(archnemesis_mod_name, 'archnemesis_mod_name', str)
        quoted_archnemesis_mod_name = '"' + archnemesis_mod_name + '"'
        if (archnemesis_mod_name not in self.archnemesis_mod_list):
            return
        self.archnemesis_mod_list.remove(archnemesis_mod_name)
        # Remove archnemesis_mod_name from rule text
        index = self.archnemesis_mod_line_index  # for convenience
        if (quoted_archnemesis_mod_name in self.text_lines[index]):
            self.text_lines[index] = '{}ArchnemesisMod {}'.format(
                    '# ' if self.visibility == RuleVisibility.kDisable else '',
                    '"' + '" "'.join(self.archnemesis_mod_list) + '"')
        # Now if the line is empty, it will generate an error in PoE,
        # so we need to comment out the rule if no archnemesis mods left
        if (len(self.archnemesis_mod_list) == 0):
            self.SetVisibility(RuleVisibility.kDisable)
            # Also, need to eliminate the ' ""'  in the list
            self.text_lines[index] = self.text_lines[index][:-3]
    # End RemoveArchnemesisMod
    
    def ClearArchnemesisModList(self):
        while (len(self.archnemesis_mod_list) > 0):
            self.RemoveArchnemesisMod(self.archnemesis_mod_list[-1])
    # End ClearArchnemesisModList
    
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
     - self.profile_config_data: dict
     - self.input_filter_fullpath: str
     - self.text_lines: List[str]
     - self.header_lines: list[str] - the lines of the loot filter up to the start of the rules
     - self.parser_index: int
     - self.rules_start_line_index: int
     - self.rule_or_comment_block_list: list[LootFilterRule or list[str]]
     - self.type_tier_rule_map: 2d dict - (type_tag, tier_tag) maps to a unique LootFilterRule
       Example: self.type_tier_rule_map['currency']['t1exalted']
    
    Old, removed or no longer using:
     - self.section_map: OrderedDict[id: str, name: str]
     - self.inverse_section_map: Dict[name: str, id: str]
     - self.section_rule_map: OrderedDict[section_name: str, List[LootFilterRule]]
     - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
    '''

    # ================================= Public API =================================
    
    # Construct LootFilter object, parsing the given loot filter file
    def __init__(self, profile_name: str, output_as_input_filter: bool):
        CheckType(profile_name, 'profile_name', str)
        CheckType(output_as_input_filter, 'output_as_input_filter', bool)
        self.profile_config_data = profile.ParseProfileConfig(profile_name)
        self.input_filter_fullpath = (self.profile_config_data['OutputLootFilterFullpath']
                if output_as_input_filter else self.profile_config_data['InputLootFilterFullpath'])
        self.ParseInputFilterFile()
    # End __init__

    def SaveToFile(self):
        with open(self.profile_config_data['OutputLootFilterFullpath'], 'w') as output_file:
            for line in self.header_lines:
                output_file.write(line + '\n')
            for rule_or_comment_block in self.rule_or_comment_block_list:
                if (isinstance(rule_or_comment_block, LootFilterRule)):
                    rule = rule_or_comment_block
                    for line in rule.text_lines:
                        output_file.write(line + '\n')
                    #output_file.writelines(rule.text_lines)
                else:
                    comment_block = rule_or_comment_block
                    for line in comment_block:
                        output_file.write(line + '\n')
                    #output_file.writelines(comment_block)
                output_file.write('\n')
            '''
            line_index: int = 0
            previous_line: str = ''
            while (line_index < len(self.text_lines)):
                line: str = self.text_lines[line_index]
                # If not a new rule start, just write input line back out
                if (not helper.IsRuleStart(self.text_lines, line_index)):
                    output_file.write(line + '\n')
                    line_index += 1
                # Otherwise is a new rule - write out the rule from line_index_rule_map
                else:  # IsRuleStart
                    # Ensure there is a blank line before each rule start
                    if (previous_line.strip() != ''):
                        output_file.write('\n')
                    rule = self.line_index_rule_map[line_index]
                    output_file.write(str(rule) + '\n')
                    line_index += len(rule.text_lines)
                previous_line = line
            '''
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
    # TODO: shouldn't this just return the rule itself?
    def GetRuleMatchingItem(self, item_text_lines: List[str]) -> Tuple[str, str]:
        CheckType2(item_text_lines, 'item_text_lines', list, str)
        item_properties: dict = rule_parser.ParseItem(item_text_lines)
        matched_continue_rule = None
        for rule_or_comment_block in self.rule_or_comment_block_list:
            if (isinstance(rule, LootFilterRule)):
                rule = rule_or_comment_block
                if ((rule.visibility != RuleVisibility.kDisable)
                        and rule.MatchesItem(item_properties)):
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
    '''   
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
    '''
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
    
    def SetFlaskRuleEnabledFor(self, flask_base_type: str, enable_flag: bool, high_ilvl_flag: bool):
        CheckType(flask_base_type, 'flask_base_type', str)
        CheckType(enable_flag, 'enable_flag', bool)
        CheckType(high_ilvl_flag, 'high_ilvl_flag', bool)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag + ('_high_ilvl' if high_ilvl_flag else '')
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        if (enable_flag):
            rule.AddBaseType(flask_base_type)
            # Rule may have been disabled if BaseType line was previously empty
            rule.SetVisibility(RuleVisibility.kShow)
        else:  # disable
            rule.RemoveBaseType(flask_base_type)
    # End SetFlaskRuleEnabledFor
    
    def IsFlaskRuleEnabledFor(self, flask_base_type: str, high_ilvl_flag: bool) -> bool:
        CheckType(flask_base_type, 'flask_base_type', str)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag + ('_high_ilvl' if high_ilvl_flag else '')
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        if (rule.visibility != RuleVisibility.kShow):
            return False
        return flask_base_type in rule.base_type_list
    # End IsFlaskRuleEnabledFor
    
    def GetAllVisibleFlaskTypes(self, high_ilvl_flag: bool) -> List[str]:
        type_tag = 'dlf_flasks'
        tier_tag = type_tag + ('_high_ilvl' if high_ilvl_flag else '')
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        if (rule.visibility != RuleVisibility.kShow):
            return []
        return rule.base_type_list
    
    # ========================= Currency-Related Functions =========================
        
    def SetCurrencyToTier(self, currency_name: str, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(target_tier, 'target_tier', int)
        # Handle single (non-stacked) currency rule
        original_tier: int = self.GetTierOfCurrency(currency_name)
        self.MoveCurrencyFromTierToTier(currency_name, original_tier, target_tier)
        # Handle stacked currency rules
        self.SetStackedCurrencyToTier(currency_name, target_tier)
    # End MoveCurrencyToTier
    
    def SetStackedCurrencyToTier(self, currency_name: str, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(target_tier, 'target_tier', int)
        # For initial implementation, we will just remove from all stacked tiers first
        # (it may not be in the same stacked tier as normal tier)
        for tier in range(1, consts.kMaxCurrencyTier + 1):
            for (type_tag, tier_tag) in consts.kStackedCurrencyTags[tier]:
                rule = self.type_tier_rule_map[type_tag][tier_tag]
                if (tier == target_tier):
                    rule.AddBaseType(currency_name)
                else:
                    rule.RemoveBaseType(currency_name)
    # End SetStackedCurrencyToTier
    
    def SetCurrencyMinVisibleStackSize(self, tier_str: str, min_stack_size_str: str):
        CheckType(tier_str, 'tier_str', str)
        CheckType(min_stack_size_str, 'min_stack_size_str', str)
        tier: int = 10 if tier_str == 'tportal' else (
                    11 if tier_str == 'twisdom' else int(tier_str))
        min_stack_size = 100 if min_stack_size_str == 'hide_all' else int(min_stack_size_str)
        valid_stack_sizes = (consts.kCurrencyStackSizes if tier >= 8
                else consts.kCurrencyStackSizes[:-1]) + [100]
        if (min_stack_size not in valid_stack_sizes):
            raise RuntimeError('min_stack_size: {} invalid, valid options are {} for tier 1-7, '
                    'or {} for tiers 8-9 and scrolls'.format(
                        min_stack_size, consts.kCurrencyStackSizes[:-1], consts.kCurrencyStackSizes))
        # Hide all stacks lower than stack_size, show all stacks greater than or equal to stack size
        # First single currency items
        type_tag = consts.kCurrencyTypeTag
        tier_tag = consts.kCurrencyTierNames[tier]
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        target_visibility = RuleVisibility.kShow if min_stack_size <= 1 else RuleVisibility.kHide
        rule.SetVisibility(target_visibility)
        # Now actual currency stacks
        for i, (type_tag, tier_tag) in enumerate(consts.kStackedCurrencyTags[tier]):
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            rule_stack_size = consts.kValidStackSizes[i + 1]
            target_visibility = (RuleVisibility.kShow if rule_stack_size >= min_stack_size
                                 else RuleVisibility.kHide)
            rule.SetVisibility(target_visibility)
    # End SetCurrencyMinVisibleStackSize
    
    # Returns a list of (stack_size, visible_flag) pairs
    def GetStackedCurrencyVisibility(self, tier_str: str) -> list:
        CheckType(tier_str, 'tier_str', str)
        tier: int = 10 if tier_str == 'tportal' else (
                    11 if tier_str == 'twisdom' else int(tier_str))
        result_list = []
        # Start with non-stacked currency (StackSize 1)
        tier_param = tier if tier < 10 else tier_str
        single_currency_visibility = self.GetCurrencyTierVisibility(tier_param)
        result_list.append((1, single_currency_visibility == RuleVisibility.kShow))
        # Actual stacks
        tag_pairs = consts.kStackedCurrencyTags[tier]
        for i, (type_tag, tier_tag) in enumerate(tag_pairs):
            stack_size = 2**(i + 1)
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            result_list.append((stack_size, rule.visibility == RuleVisibility.kShow))
        return result_list
    # End GetStackedCurrencyVisibility
    
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
    
    # Returns the integer tier to which the given currency belongs
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
        target_currency_rule.Enable()
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
        for tier in range(1, consts.kMaxCurrencyTier + 1):
            visibility = RuleVisibility.kHide if tier > max_visible_tier else RuleVisibility.kShow
            self.SetCurrencyTierVisibility(tier, visibility)
    # SetHideCurrencyAboveTierTier
    
    def GetHideCurrencyAboveTierTier(self) -> int:
        max_visible_tier: int = 0
        for tier in range(1, consts.kMaxCurrencyTier + 1):
            if (self.GetCurrencyTierVisibility(tier) == RuleVisibility.kShow):
                max_visible_tier = tier
            else:
                break
        return max_visible_tier
    # GetHideCurrencyAboveTierTier
    
    # =========================== Archnemesis Functions ===========================
    
    # Note: highest tier = hide
    def SetArchnemesisModToTier(self, archnemesis_mod: str, target_tier: int):
        CheckType(archnemesis_mod, 'archnemesis_mod', str)
        CheckType(target_tier, 'target_tier', int)
        for tier in range(1, consts.kNumArchnemesisTiers):  # exclude last tier because it's hide all
            type_tag, tier_tag = consts.kArchnemesisTags[tier]
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            if (tier != target_tier):
                rule.RemoveArchnemesisMod(archnemesis_mod)
            else:
                rule.AddArchnemesisMod(archnemesis_mod)
                rule.Enable()
    # End SetArchnemesisModToTier
    
    def GetAllArchnemesisModsInTier(self, tier: int) -> list:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kArchnemesisTags[tier]
        return self.type_tier_rule_map[type_tag][tier_tag].archnemesis_mod_list
    # End GetAllArchnemesisModsInTier
    
    # ============================= Essence Functions =============================
    
    def SetEssenceTierVisibility(self, tier: int, visibility: RuleVisibility):
        CheckType(tier, 'tier', int)
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag, tier_tag = consts.kEssenceTags[tier]
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        rule.SetVisibility(visibility)
    # SetEssenceTierVisibility
    
    def GetEssenceTierVisibility(self, tier: int) -> RuleVisibility:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kEssenceTags[tier]
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        return rule.visibility
    # GetUniqueTierVisibility
    
    def SetHideEssencesAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kNumEssenceTiers + 1):
            visibility = RuleVisibility.kHide if tier > max_visible_tier else RuleVisibility.kShow
            self.SetEssenceTierVisibility(tier, visibility)
    # SetHideEssencesAboveTierTier
    
    def GetHideEssencesAboveTierTier(self) -> int:
        max_visible_tier: int = 0
        for tier in range(1, consts.kNumEssenceTiers + 1):
            if (self.GetEssenceTierVisibility(tier) == RuleVisibility.kShow):
                max_visible_tier = tier
            else:
                break
        return max_visible_tier
    # GetHideEssencesAboveTierTier
    
    # ============================= Div Card Functions =============================
    
    def SetDivCardTierVisibility(self, tier: int, visibility: RuleVisibility):
        CheckType(tier, 'tier', int)
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag, tier_tag = consts.kDivCardTags[tier]
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        rule.SetVisibility(visibility)
    # SetDivCardTierVisibility
    
    def GetDivCardTierVisibility(self, tier: int) -> RuleVisibility:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kDivCardTags[tier]
        rule = self.type_tier_rule_map[type_tag][tier_tag]
        return rule.visibility
    # GetDivCardTierVisibility
    
    def SetHideDivCardsAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kNumDivCardTiers + 1):
            visibility = RuleVisibility.kHide if tier > max_visible_tier else RuleVisibility.kShow
            self.SetDivCardTierVisibility(tier, visibility)
    # SetHideDivCardAboveTierTier
    
    def GetHideDivCardsAboveTierTier(self) -> int:
        max_visible_tier: int = 0
        for tier in range(1, consts.kNumDivCardTiers + 1):
            if (self.GetDivCardTierVisibility(tier) == RuleVisibility.kShow):
                max_visible_tier = tier
            else:
                break
        return max_visible_tier
    # GetHideDivCardAboveTierTier
    
    # =========================== Oil-Related Functions ===========================
    
    def SetLowestVisibleOil(self, lowest_visible_oil_name: str):
        type_tag = consts.kOilTypeTag
        visible_flag = True
        for oil_name, tier in consts.kOilTierList:
            tier_tag = 't' + str(tier)
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            if (visible_flag):
                rule.AddBaseType(oil_name)
                rule.Enable()
            else:
                rule.RemoveBaseType(oil_name)
            if (oil_name == lowest_visible_oil_name):
                visible_flag = False  # hide rest below this oil
    # End SetLowestVisibleOil
    
    def GetLowestVisibleOil(self) -> str:
        type_tag = consts.kOilTypeTag
        # Iterate upwards from bottom oil to find first visible
        for oil_name, tier in reversed(consts.kOilTierList):
            tier_tag = 't' + str(tier)
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            if (oil_name in rule.base_type_list):
                return oil_name
    # End GetLowestVisibleOil
    
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
        for tier in range(1, consts.kNumUniqueTiers + 1):
            visibility = RuleVisibility.kHide if tier > max_visible_tier else RuleVisibility.kShow
            self.SetUniqueTierVisibility(tier, visibility)
    # SetHideUniquesAboveTierTier
    
    def GetHideUniquesAboveTierTier(self) -> int:
        max_visible_tier: int = 0
        for tier in range(1, consts.kNumUniqueTiers + 1):
            if (self.GetUniqueTierVisibility(tier) == RuleVisibility.kShow):
                max_visible_tier = tier
            else:
                break
        return max_visible_tier
    # GetHideUniquesAboveTierTier
    
    # ============================ Gem Quality Functions ============================
    
    # The rules we modify for gem quality functionality are:
    #  - Show # %D5 $type->gems-generic $tier->qt2   (19-20)
    #  - Show # %D3 $type->gems-generic $tier->qt3   (14-18)
    #  - Show # %D2 $type->gems-generic $tier->qt4   (1-13)
    def SetGemMinQuality(self, min_quality: int):
        CheckType(min_quality, 'min_quality', int)
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
    
    # ============================ Flask Quality Functions ============================
    
    # The rules we modify for flask quality functionality are:
    #  - Show # %D5 $type->endgameflasks $tier->qualityhigh  (14-20)
    #  - Show # %D3 $type->endgameflasks $tier->qualitylow   (1-13)
    # Note: any min_quality value outside the range [1, 20] will disable all flask quality rules
    def SetFlaskMinQuality(self, min_quality: int):
        CheckType(min_quality, 'min_quality', int)
        type_tag: str = 'endgameflasks'
        quality_high_rule = self.type_tier_rule_map[type_tag]['qualityhigh']
        quality_low_rule = self.type_tier_rule_map[type_tag]['qualitylow']
        if (14 <= min_quality <= 20):
            quality_high_rule.SetVisibility(RuleVisibility.kShow)
            quality_high_rule.ModifyLine('Quality', '>=', min_quality)
            quality_low_rule.SetVisibility(RuleVisibility.kDisable)
        elif (1 <= min_quality <= 13):
            quality_high_rule.SetVisibility(RuleVisibility.kShow)
            quality_high_rule.ModifyLine('Quality', '>=', 14)
            quality_low_rule.SetVisibility(RuleVisibility.kShow)
            quality_low_rule.ModifyLine('Quality', '>=', min_quality)        
        else:  # out of range [1, 20] --> disable all flask quality rules
            quality_high_rule.SetVisibility(RuleVisibility.kDisable)
            quality_low_rule.SetVisibility(RuleVisibility.kDisable)
    # End SetFlaskMinQuality
    
    def GetFlaskMinQuality(self):
        type_tag: str = 'endgameflasks'
        tier_tag_list: list[str] = ['qualitylow', 'qualityhigh']
        for tier_tag in tier_tag_list:
            rule = self.type_tier_rule_map[type_tag][tier_tag]
            if (rule.visibility == RuleVisibility.kShow):
                for keyword, operator, value_string_list in rule.parsed_lines:
                    if keyword == 'Quality':
                        return int(value_string_list[0])
        return -1  # indicates all flask quality rules are disabled/hidden
    
    # ============================== RGB Item Functions ==============================
    def SetRgbItemMaxSize(self, max_size_string: str):
        CheckType(max_size_string, 'max_size_string', str)
        type_tag = consts.kRgbTypeTag
        if (max_size_string not in consts.kRgbSizesMap):
            raise RuntimeError('Invalid max_size_string: "{}", expected one of {}'.format(
                    max_size_string, consts.kRgbSizesMap.keys()))
        max_size_int, _ = consts.kRgbSizesMap[max_size_string]
        for _, (size_int, tier_tag_list) in consts.kRgbSizesMap.items():
            for tier_tag in tier_tag_list:
                target_visibility = (RuleVisibility.kShow if size_int <= max_size_int
                                     else RuleVisibility.kHide)
                self.type_tier_rule_map[type_tag][tier_tag].SetVisibility(
                        target_visibility)
    # End SetRgbItemMaxSize
    
    def GetRgbItemMaxSize(self) -> str:
        type_tag = consts.kRgbTypeTag
        max_size_string = 'none'
        max_size_int = 0
        for size_string, (size_int, tier_tag_list) in consts.kRgbSizesMap.items():
            for tier_tag in tier_tag_list:
                rule = self.type_tier_rule_map[type_tag][tier_tag]
                if ((size_int > max_size_int) and (rule.visibility == RuleVisibility.kShow)):
                    max_size_string = size_string
                    max_size_int = size_int
        return max_size_string
    # End GetRgbItemMaxSize
    
    # ======================== Chaos Recipe-Related Functions ========================
    
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
        self.header_lines = self.text_lines[: self.rules_start_line_index]
        self.parser_index = self.rules_start_line_index
        # Add custom user-defiend rules plus DLF-generated rules like chaos recipe rules
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
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int,
                'Custom rules from ' + self.profile_config_data['ProfileName'] + '.rules')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        custom_rules_lines = helper.ReadFile(self.profile_config_data['RulesFullpath'])
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
                self.profile_config_data['HideMapsBelowTier'])
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Add flask rules
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Show specific flask BaseTypes')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        to_add_string = consts.kFlaskRuleTemplate
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        to_add_string = consts.kHighIlvlFlaskRuleTemplate
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Add chaos recipe rules
        # TODO: comment out if config says don't add chaos recipe rules
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Show chaos recipe rares by item +slot')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Weapons handled separately, since config tells us which classes to use
        item_slot = 'WeaponsX'
        weapon_classes = self.profile_config_data['ChaosRecipeWeaponClassesAnyHeight']
        to_add_string = consts.GenerateChaosRecipeWeaponRule(item_slot, weapon_classes)
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        item_slot = 'Weapons3'
        weapon_classes = self.profile_config_data['ChaosRecipeWeaponClassesMaxHeight3']
        to_add_string = consts.GenerateChaosRecipeWeaponRule(item_slot, weapon_classes)
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Handle the rest of chaos recipe rules
        for chaos_recipe_rule_string in consts.kChaosRecipeRuleStrings:
            to_add_string_list.extend(chaos_recipe_rule_string.split('\n') + [''])
        # Add Archnemesis rules
        current_section_id_int += 1
        to_add_string = consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Highlight specific Archnemesis ingredients')
        to_add_string_list.extend(to_add_string.split('\n') + [''])
        for archnemesis_rule_template in consts.kArchnemesisRuleTemplates:
            to_add_string = archnemesis_rule_template
            to_add_string_list.extend(to_add_string.split('\n') + [''])
        # Update self.text_lines to contain the newly added rules
        # Python trick to insert one list into another: https://stackoverflow.com/a/5805910
        insert_index: int = self.rules_start_line_index
        self.text_lines[insert_index : insert_index] = to_add_string_list
    # End AddDlfRulesIfMissing
    
    def ParseLootFilterRules(self) -> None:
        '''
        This function parses self.text_lines into:
         - self.rule_or_comment_block_list: list[LootFilterRule or list[str]]
         - self.type_tier_rule_map: 2d dict - (type_tag, tier_tag) maps to a unique LootFilterRule
           Note: parser ensures that (type_tag, tier_tag) forms a unique key for rules
           Example: self.type_tier_rule_map['currency']['t1'] 
        '''
        # Initialize data structures to store parsed data
        self.rule_or_comment_block_list = []
        self.type_tier_rule_map = {}
        # Set up parsing loop
        current_block: list[str] = []
        untagged_rule_count = 0
        while (self.parser_index < len(self.text_lines)):
            current_line = self.text_lines[self.parser_index]
            # Check for end of block
            if ((current_line.strip() == '') and (len(current_block) > 0)):
                is_comment_block: bool = (helper.FindTagLineIndex(current_block) == -1)
                if (is_comment_block):
                    self.rule_or_comment_block_list.append(current_block)
                else:  # is rule
                    new_rule = LootFilterRule(current_block, self.parser_index - len(current_block))
                    # Generate unique type-tier tag pair if no tags
                    # (For now we assume it either has both or none)
                    if ((new_rule.type_tag == '') and (new_rule.tier_tag == '')):
                        new_rule.type_tag = 'untagged_rule'
                        new_rule.tier_tag = str(untagged_rule_count)
                        new_rule.AddTypeTierTags(new_rule.type_tag, new_rule.tier_tag)
                        untagged_rule_count += 1
                    # Add rule to type tier rule map
                    if (new_rule.type_tag not in self.type_tier_rule_map):
                        self.type_tier_rule_map[new_rule.type_tag] = {}
                    self.type_tier_rule_map[new_rule.type_tag][new_rule.tier_tag] = new_rule
                    # Add rule to rule orStacked Cu comment block list
                    self.rule_or_comment_block_list.append(new_rule)
                current_block = []
            else:  # not end of block
                current_block.append(current_line)
            self.parser_index += 1
    # End ParseLootFilterRules
    
    # Apply changes that need to be made to the filter on import only
    def ApplyImportChanges(self):
        # Place oils in appropriate tiers
        oil_hide_rule = self.type_tier_rule_map[consts.kOilTypeTag][consts.kOilHideTierTag]
        oil_hide_rule.SetVisibility(RuleVisibility.kHide)
        for oil_tier in range(1, consts.kMaxOilTier + 1):
            rule = self.type_tier_rule_map[consts.kOilTypeTag]['t' + str(oil_tier)]
            rule.ClearBaseTypeList()
        for oil_name, oil_tier in consts.kOilTierList:
            rule = self.type_tier_rule_map[consts.kOilTypeTag]['t' + str(oil_tier)]
            rule.AddBaseType(oil_name)
            rule.SetVisibility(RuleVisibility.kShow)
        # Set currency stack size thresholds to 2, 4, 8
        for tier, tag_pairs in consts.kStackedCurrencyTags.items():
            for i, (type_tag, tier_tag) in enumerate(tag_pairs):
                stack_size = consts.kCurrencyStackSizes[i + 1]
                rule = self.type_tier_rule_map[type_tag][tier_tag]
                # Find "StackSize" line and rewrite stack size threshold
                for j in range(len(rule.text_lines)):
                    if ('StackSize' in rule.text_lines[j]):
                        rule.text_lines[j] = 'StackSize >= {}'.format(stack_size)
    # End ApplyImportChanges

# -----------------------------------------------------------------------------
