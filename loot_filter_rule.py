from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Tuple

from hash_linked_list import HashLinkedList
import logger
import parse_helper
import profile
import rule_parser
from type_checker import CheckType

kTypeIdentifier = '$type->'
kTierIdentifier = '$tier->'

class RuleVisibility(Enum):
    kShow = 1
    kHide = 2
    kDisabledShow = 3  # rule is commented out
    kDisabledHide = 4  # rule is commented out
    kDisabledAny = 5  # used as input parameter to set visibility only
    # kDisabledAny will never be the visibility state of a rule
    kUnknown = 6
    
    # Note: both IsEnabled and IsDisabled could be false if the value is kUnknown.
    
    @staticmethod
    def IsEnabled(visibility) -> bool:
        return visibility in (RuleVisibility.kShow, RuleVisibility.kHide)
    # End IsEnabled
    
    @staticmethod
    def IsDisabled(visibility) -> bool:
        return visibility in (RuleVisibility.kDisabledShow,
                RuleVisibility.kDisabledHide, RuleVisibility.kDisabledAny)
    # End IsDisabled
    
    @staticmethod
    def IsShow(visibility) -> bool:
        return visibility in (RuleVisibility.kShow, RuleVisibility.kDisabledShow)
    # End IsShow
    
    @staticmethod
    def IsHide(visibility) -> bool:
        return visibility in (RuleVisibility.kHide, RuleVisibility.kDisabledHide)
    # End IsHide

# End class RuleVisibility

# -----------------------------------------------------------------------------

class LootFilterRule:
    '''
    Member variables:
     - self.header_comment_lines: List[str] - all lines before the Show/Hide/Disable line
     - self.rule_text_lines: List[str] - text lines excluding header comment lines
     - self.parsed_lines_hll: hash_linked_list mapping keyword to (operator, values_list) pairs
        - keyword: str, operator: str, value_list: List[str]
     - self.visibility: RuleVisibility
     - self.type_tag: str - identifier found after "$type->" in the first line of the rule
     - self.tier_tag: str - identifier found after "$tier->" in the first line of the rule
        - Tags will be None (but contructor will not error) if tags do not exist in input text
    '''

    # We define a block of text lines to be parsable as a LootFilterRule
    # if it contains a Show/Hide line, as defined by parse_helper.FindShowHideLineIndex.
    # If this function returns True, the LootFilterRule constructor is guaranteed not to
    # raise an error on the same input.
    @staticmethod
    def IsParsableAsRule(text_lines: List[str] or str):
        if (isinstance(text_lines, str)):
            text_lines = text_lines.split('\n')
        CheckType(text_lines, 'text_lines', list, str)
        return parse_helper.FindShowHideLineIndex(text_lines) != None

    def __init__(self, text_lines: List[str] or str):
        if (isinstance(text_lines, str)):
            text_lines = text_lines.split('\n')
        CheckType(text_lines, 'text_lines', list, str)
        if (not LootFilterRule.IsParsableAsRule(text_lines)):
            raise RuntimeError('given text_lines cannot be parsed as a LootFilterRule:\n'
                    '{}'.format(text_lines))
        # Find the index of the line containing Show/Hide
        # Everything above that line should be commented, and is assigned to self.header_comment_lines
        show_hide_line_index = parse_helper.FindShowHideLineIndex(text_lines)
        if (show_hide_line_index == None):
            raise RuntimeError('did not find Show/Hide line in rule:\n{}'.format(text_lines))
        for i in range(show_hide_line_index):
            if (not parse_helper.IsCommented(text_lines[i])):
                raise RuntimeError('Header line is not commented: {}'.format(text_lines[i]))
        self.header_comment_lines = text_lines[:show_hide_line_index]
        self.rule_text_lines = text_lines[show_hide_line_index:]
        tags = parse_helper.ParseTypeTierTags(self.rule_text_lines)
        self.type_tag, self.tier_tag = tags if (tags != None) else (None, None)
        self.ParseRuleTextLines()
    # End __init__
    
    # Call in constructor or when self.rule_text_lines changes.
    # Updates the rest of the member variables to be consistent with rule_text_lines.
    def ParseRuleTextLines(self):
        # Generate self.parsed_lines_hll HashLinkedList
        self.parsed_lines_hll = HashLinkedList()
        # We don't save the Show/Hide line in the hll, because it would add complexity to update
        for line in self.rule_text_lines[1:]:
            keyword, operator, values_list = rule_parser.ParseRuleLineGeneric(line)
            self.parsed_lines_hll.append(keyword, (operator, values_list))
        # Parse rule visibility
        cleaned_show_hide_line = parse_helper.UncommentedLine(self.rule_text_lines[0]).strip()
        if (not (cleaned_show_hide_line.startswith('Show') or cleaned_show_hide_line.startswith('Hide'))):
            raise RuntimeError('Show/Hide line invalid: {}'.format(self.rule_text_lines[0]))
        is_show: bool = cleaned_show_hide_line.startswith('Show')
        is_enabled: bool = not all(parse_helper.IsCommented(line) for line in self.rule_text_lines)
        self.visibility = RuleVisibility.kUnknown
        if (is_show and is_enabled):
            self.visibility = RuleVisibility.kShow
        elif (not is_show and is_enabled):
            self.visibility = RuleVisibility.kHide
        elif (is_show and not is_enabled):
            self.visibility = RuleVisibility.kDisabledShow
        elif (not is_show and not is_enabled):
            self.visibility = RuleVisibility.kDisabledHide
    # End ParseTextLines
    
    # Call when a change is made to the object's state (other than rule_text_lines).
    # Updates self.rule_text_lines to be consistent with the rest of the member variables.
    def UpdateRuleTextLines(self):
        self.rule_text_lines = []
        # The Show/Hide line is not in the hll, so we first add it directly
        tag_line = '# ' if RuleVisibility.IsDisabled(self.visibility) else ''
        tag_line += 'Show' if RuleVisibility.IsShow(self.visibility) else 'Hide'
        tag_line += ' # ' + kTypeIdentifier + self.type_tag
        tag_line += ' ' + kTierIdentifier + self.tier_tag
        self.rule_text_lines.append(tag_line)
        # Construct and append all lines from hll
        # If rule is Hide, disable beams, minimap icons, and drop sounds
        keywords_to_disable = (['PlayEffect', 'MinimapIcon', 'PlayAlertSound']
                if self.visibility == RuleVisibility.kHide else [])
        for keyword, (operator, values_list) in self.parsed_lines_hll:
            line = ('# ' if RuleVisibility.IsDisabled(self.visibility)
                    or (keyword in keywords_to_disable) else '')
            line += keyword
            if (operator != ''):
                line += ' ' + operator
            values_string = parse_helper.ConvertValuesListToString(values_list)
            if (values_string != ''):
                line += ' ' + values_string
            self.rule_text_lines.append(line)
    # End GenerateRuleTextLines
    
    def __repr__(self):
        raw_rule_text = '\n'.join(self.header_comment_lines + self.rule_text_lines)
        hll_as_text = '\n'.join(str((k, o, v)) for k, (o, v) in self.parsed_lines_hll)
        return 'Raw Rule Text:\n' + raw_rule_text + '\n\nHash Linked List:\n' + hll_as_text + '\n'
    # End __repr__
    
    # Sets type and tier tags and updates the rule text lines accordingly
    def SetTypeTierTags(self, type_tag: str, tier_tag: str):
        CheckType(type_tag, 'type_tag', str)
        CheckType(tier_tag, 'tier_tag', str)
        self.type_tag = type_tag
        self.tier_tag = tier_tag
        self.UpdateRuleTextLines()
    # End SetTypeTierTags
    
    # TODO: we changed the format of self.parsed_lines, so this no longer works.
    def MatchesItem(self, item_properties: dict) -> bool:
        return rule_parser.CheckRuleMatchesItem(self.parsed_lines, item_properties)
    # End MatchesItem
    
    # Uncomments the rule if it is commented.
    def Enable(self):
        if (RuleVisibility.IsDisabled(self.visibility)):
            is_show = RuleVisibility.IsShow(self.visibility)
            self.visibility = RuleVisibility.kShow if is_show else RuleVisibility.kHide
            self.UpdateRuleTextLines()
    # End Enable
    
    # Comments the rule if it is not commented already.
    def Disable(self):
        if (RuleVisibility.IsEnabled(self.visibility)):
            is_show = RuleVisibility.IsShow(self.visibility)
            self.visibility = RuleVisibility.kDisabledShow if is_show else RuleVisibility.kDisabledHide
            self.UpdateRuleTextLines()
    # End Disable
    
    def Show(self):
        self.Enable()
        if (self.visibility == RuleVisibility.kShow):
            return
        elif (self.visibility == RuleVisibility.kHide):
            self.visibility = RuleVisibility.kShow
            self.UpdateRuleTextLines()
    # End Show
    
    def Hide(self):
        self.Enable()
        if (self.visibility == RuleVisibility.kHide):
            return
        elif (self.visibility == RuleVisibility.kShow):
            self.visibility = RuleVisibility.kHide
            self.UpdateRuleTextLines()
    # End Hide
    
    # Assumes visibility argument is either kShow, kHide, or kDisabledAny.
    def SetVisibility(self, visibility):
        if (RuleVisibility.IsDisabled(visibility)):
            self.Disable()
        elif (visibility == RuleVisibility.kShow):
            self.Show()
        elif (visibility == RuleVisibility.kHide):
            self.Hide()
        else:
            raise RuntimeError('Unsupported argument passed to SetVisibility: '
                    '{}'.format(visibility))
    # End SetVisibility
    
    def GetBaseTypeList(self) -> List[str]:
        if ('BaseType' not in self.parsed_lines_hll):
            return []
        op, base_type_list = self.parsed_lines_hll['BaseType']
        return base_type_list
    # End GetBaseTypeList
    
    # Adds base_type_name to this rule's BaseType line, if it's not there already.
    # Does not enable the rule if it is disabled. Callers should call Enable() after
    # if they expect the rule to be enabled.
    # Note: BaseType names are *not* quoted in base_type_list.
    def AddBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        if ('BaseType' not in self.parsed_lines_hll):
            self.parsed_lines_hll.insert_at_index('BaseType', ('', []), index=0)
        base_type_list = self.GetBaseTypeList()
        if (base_type_name in base_type_list):
            return
        base_type_list.append(base_type_name)
        self.UpdateRuleTextLines()
    # End AddBaseType
    
    def AddBaseTypes(self, base_type_list: list):
        CheckType(base_type_list, 'base_type_list', list, str)
        for base_type_name in base_type_list:
            self.AddBaseType(base_type_name)
    # End AddBaseTypes
    
    # Removes base_type_name from this rule's BaseType line, if it's there.
    # Does nothing if given base_type_name is not present, or rule does not have a BaseType line.
    # If this results in an empty base type list, disables the rule (otherwise PoE generates error).
    def RemoveBaseType(self, base_type_name: str):
        CheckType(base_type_name, 'base_type_name', str)
        if ('BaseType' not in self.parsed_lines_hll):
            return
        base_type_list = self.GetBaseTypeList()
        quoted_base_type_name = '"' + base_type_name + '"'
        # Check raw (unquoted) BaseType name
        if (base_type_name in base_type_list):
            base_type_list.remove(base_type_name)
        # Check quoted BaseType name
        elif (quoted_base_type_name in base_type_list):
            base_type_list.remove(quoted_base_type_name)
        else:
            return
        # If we didn't return (i.e. made a change), check for empty BaseType list and update rules text
        if (len(base_type_list) == 0):
            self.Disable()
        self.UpdateRuleTextLines()
    # End RemoveBaseType
    
    # Note: This disables the rule, since an empty BaseType line generates an error in PoE.
    def ClearBaseTypeList(self):
        base_type_list = self.GetBaseTypeList()
        while (len(base_type_list) > 0):
            self.RemoveBaseType(base_type_list[-1])
    # End ClearBaseTypeList
    
    # Returns a bool indicating whether or not the line identified by the given keyword was found
    # Updates both parsed_item_lines and text_lines
    def ModifyLine(self, keyword: str, new_operator: str,
                   new_value_or_values: str or int or list[str]) -> bool:
        CheckType(keyword, 'keyword', str)
        CheckType(new_operator, 'new_operator', str)
        CheckType(new_value_or_values, 'new_value_or_values', (str, int, list))
        if (keyword not in self.parsed_lines_hll):
            return False
        new_values = (new_value_or_values if isinstance(new_value_or_values, list)
                else [str(new_value_or_values)])
        self.parsed_lines_hll[keyword] = (new_operator, new_values)
        self.UpdateRuleTextLines()
        return True
    # End ModifyLine
    
# End class LootFilterRule