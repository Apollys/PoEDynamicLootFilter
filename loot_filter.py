from enum import Enum
from typing import List, Tuple

import consts
import file_helper
from hash_linked_list import HllNode, HashLinkedList
import logger
from loot_filter_rule import RuleVisibility, LootFilterRule
import os.path
import parse_helper
from profile import Profile
import rule_parser
from type_checker import CheckType

kTextBlockKey = 'text_block'


class InputFilterSource(Enum):
    kDownload = 1
    kInput = 2
    kOutput = 3
# End class InputFilterSource

# Holds either a LootFilterRule or a list of strings
class RuleOrTextBlock:
    '''
    Member variables:
     - self.is_rule: bool
     - self.rule: LootFilterRule
     - self.text_lines: List[str]
    '''
    
    def __init__(self, rule_or_text_block, is_rule: bool):
        CheckType(is_rule, 'is_rule', bool)
        self.is_rule = is_rule
        if (is_rule):
            CheckType(rule_or_text_block, 'rule_or_text_block', LootFilterRule)
            self.rule = rule_or_text_block
        else:
            CheckType(rule_or_text_block, 'rule_or_text_block', list, str)
            self.text_lines = rule_or_text_block
    # End __init__
# End class RuleOrTextLines

class LootFilter:
    '''
    Member variables:
     - self.profile_obj: Profile
     - self.input_filter_source: InputFilterSource
     - self.rule_or_text_block_hll: HashLinkedList mapping a key to RuleOrTextBlock
        - in the case of a LootFilterRule, the key is (type_tag, tier_tag)
        - in the case of text block, the key is (kTextBlockKey, id) where id is a unique integer
     - self.num_raw_text_blocks: int
        - used to create unique keys for raw text blocks
     - self.num_untagged_rules: int
        - used to create unique tags for untagged rules
    '''

    # ================================= Public API =================================
    
    # Construct the LootFilter, parsing the file indicated by the config values of
    # the given profile and the value of input_filter_source.
    def __init__(self, profile_param: Profile or str, input_filter_source: InputFilterSource):
        CheckType(profile_param, 'profile_param', (Profile, str))
        CheckType(input_filter_source, 'input_filter_source', InputFilterSource)
        self.profile_obj = (profile_param if isinstance(profile_param, Profile)
                else Profile(profile_param))
        # Copy/move Download filter to Input filter if appropriate
        config_values = self.profile_obj.config_values
        self.input_filter_source = input_filter_source
        if (self.input_filter_source == InputFilterSource.kDownload):
            file_helper.CopyFile(config_values['DownloadedLootFilterFullpath'],
                    config_values['InputLootFilterFullpath'])
            if (config_values['RemoveDownloadedFilter']):
                file_helper.RemoveFileIfExists(config_values['DownloadedLootFilterFullpath'])
        # Initialize remaining member variables and parse input filter
        self.rule_or_text_block_hll = HashLinkedList()
        self.num_raw_text_blocks = 0
        self.num_untagged_rules = 0
        self.ParseInputFilterFile()
    # End __init__

    def SaveToFile(self):
        with open(self.profile_obj.config_values['OutputLootFilterFullpath'],
                'w', encoding='utf-8') as output_file:
            for key, rule_or_text_block in self.rule_or_text_block_hll:
                text_lines = (rule_or_text_block.rule.rule_text_lines
                        if rule_or_text_block.is_rule else rule_or_text_block.text_lines)
                output_file.write('\n'.join(text_lines) + '\n\n')
    # End SaveToFile

    # Note: when parsing, we create unique tags for rules missing tags.
    # Rules not missing tags are assumed to have unique (type_tag, tier_tag) keys.
    def GetRule(self, type_tag: str, tier_tag: str) -> LootFilterRule:
        CheckType(type_tag, 'type_tag', str)
        CheckType(tier_tag, 'tier_tag', str)
        return self.rule_or_text_block_hll[(type_tag, tier_tag)].rule
    # End GetRule

    # ============================= Rule-Item Matching =============================
    
    # TODO: This is probably broken with the refactor.
    # Returns the first non-Continue rule in the filter matching the given item,
    # None if no rule matches the item, or the last matched Continue rule otherwise.
    # If a rule has an AreaLevel requirement, it will never match any item.
    def GetRuleMatchingItem(self, item_text_lines: List[str]) -> LootFilterRule:
        CheckType(item_text_lines, 'item_text_lines', list, str)
        item_properties: dict = rule_parser.ParseItem(item_text_lines)
        matched_continue_rule = None
        for rule_or_comment_block in self.rule_or_comment_block_list:
            if (isinstance(rule_or_comment_block, LootFilterRule)):
                rule = rule_or_comment_block
                if ((rule.visibility != RuleVisibility.kDisable)
                        and rule.MatchesItem(item_properties)):
                    if (rule.has_continue):
                        matched_continue_rule = rule
                    else:
                        return rule
        if (matched_continue_rule):
            return matched_continue_rule
        return None
    # End GetRuleMatchingItem
    
    # =========================== Map-Related Functions ===========================
    
    def SetHideMapsBelowTierTier(self, tier: int) -> int:
        CheckType(tier, 'tier', int)
        type_name = 'dlf_hide_maps_below_tier'
        tier_name = type_name
        rule = self.GetRule(type_name, tier_name)
        rule.ModifyLine('MapTier', '<', tier)
    # End SetHideMapsBelowTierTier
    
    def GetHideMapsBelowTierTier(self) -> int:
        type_name = 'dlf_hide_maps_below_tier'
        tier_name = type_name
        rule = self.GetRule(type_name, tier_name)
        op, [tier_str] = rule.parsed_lines_hll['MapTier']
        return int(tier_str)
    # End GetHideMapsBelowTierTier
    
    # =========================== Generic BaseType Functions ==========================
    
    # The rare_only_flag should only be specified when enable_flag is True.
    # When enable_flag is False, the base_type is removed from both rules.
    def SetBaseTypeRuleEnabledFor(self, base_type: str, enable_flag: bool, rare_only_flag: bool = False):
        CheckType(base_type, 'base_type', str)
        CheckType(enable_flag, 'enable_flag', bool)
        CheckType(rare_only_flag, 'rare_only_flag', bool)
        # If enabling, start by disabling from all rules for a clean slate
        if (enable_flag):
            self.SetBaseTypeRuleEnabledFor(base_type, enable_flag=False)
        type_tag = consts.kBaseTypeTypeTag
        rare_tier_tag = consts.kBaseTypeTierTagRare
        any_tier_tag = consts.kBaseTypeTierTagAny
        rules = [self.GetRule(type_tag, rare_tier_tag)]
        if (not rare_only_flag):
            rules.append(self.GetRule(type_tag, any_tier_tag))
        for rule in rules:
            if (enable_flag):
                rule.AddBaseType(base_type)
                rule.Enable()
            else:
                rule.RemoveBaseType(base_type)
    # End SetBaseTypeRuleEnabledFor
    
    # If rare_flag is True, checks the rare rule.
    # If rare_flag is False, checks the any non-unique rule.
    def IsBaseTypeRuleEnabledFor(self, base_type: str, rare_flag: bool) -> bool:
        CheckType(base_type, 'base_type', str)
        CheckType(rare_flag, 'rare_flag', bool)
        type_tag = consts.kBaseTypeTypeTag
        tier_tag = consts.kBaseTypeTierTagRare if rare_flag else consts.kBaseTypeTierTagAny
        rule = self.GetRule(type_tag, tier_tag)
        if (rule.visibility != RuleVisibility.kShow):
            return False
        return base_type in rule.GetBaseTypeList()
    # End IsBaseTypeRuleEnabledFor
    
    # If rare_flag is True, checks the rare rule.
    # If rare_flag is False, checks the any non-unique rule.
    def GetAllVisibleBaseTypes(self, rare_flag: bool) -> List[str]:
        CheckType(rare_flag, 'rare_flag', bool)
        type_tag = consts.kBaseTypeTypeTag
        tier_tag = consts.kBaseTypeTierTagRare if rare_flag else consts.kBaseTypeTierTagAny
        rule = self.GetRule(type_tag, tier_tag)
        if (rule.visibility != RuleVisibility.kShow):
            return []
        return rule.GetBaseTypeList()
    
    # =========================== Flask BaseType Functions ==========================
    
    def SetFlaskRuleEnabledFor(self, flask_base_type: str, enable_flag: bool, high_ilvl_flag: bool):
        CheckType(flask_base_type, 'flask_base_type', str)
        CheckType(enable_flag, 'enable_flag', bool)
        CheckType(high_ilvl_flag, 'high_ilvl_flag', bool)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag + ('_high_ilvl' if high_ilvl_flag else '')
        rule = self.GetRule(type_tag, tier_tag)
        if (enable_flag):
            rule.AddBaseType(flask_base_type)
            # Rule may have been disabled if BaseType line was previously empty
            rule.Enable()
        else:
            rule.RemoveBaseType(flask_base_type)
    # End SetFlaskRuleEnabledFor
    
    def IsFlaskRuleEnabledFor(self, flask_base_type: str, high_ilvl_flag: bool) -> bool:
        CheckType(flask_base_type, 'flask_base_type', str)
        CheckType(high_ilvl_flag, 'high_ilvl_flag', bool)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag + ('_high_ilvl' if high_ilvl_flag else '')
        rule = self.GetRule(type_tag, tier_tag)
        if (rule.visibility != RuleVisibility.kShow):
            return False
        return flask_base_type in rule.GetBaseTypeList()
    # End IsFlaskRuleEnabledFor
    
    def GetAllVisibleFlaskTypes(self, high_ilvl_flag: bool) -> List[str]:
        CheckType(high_ilvl_flag, 'high_ilvl_flag', bool)
        type_tag = 'dlf_flasks'
        tier_tag = type_tag + ('_high_ilvl' if high_ilvl_flag else '')
        rule = self.GetRule(type_tag, tier_tag)
        if (rule.visibility != RuleVisibility.kShow):
            return []
        return rule.GetBaseTypeList()
    
    # ========================= Currency-Related Functions =========================
    
    # Note: currency-related functions assume that stacked and unstacked currency tiers
    # are consistent.  This condition is enforced upon import and maintained within
    # all currency tier modification functions.
    
    # Sets the specified currency to the given tier, in unstacked and all stacked rules.
    def SetCurrencyToTier(self, currency_name: str, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(target_tier, 'target_tier', int)
        original_tier: int = self.GetTierOfCurrency(currency_name)
        self.MoveCurrencyFromTierToTier(currency_name, original_tier, target_tier)
    # End MoveCurrencyToTier
    
    # Returns the integer tier to which the given currency belongs.
    # (Result is based on the unstacked currency rules, but since tier
    # consistency is enforced, this is only an implementation detail.)
    def GetTierOfCurrency(self, currency_name: str) -> int:
        CheckType(currency_name, 'currency_name', str)
        for tier in range(1, consts.kNumCurrencyTiersIncludingScrolls + 1):
            stack_size = 1
            type_tag, tier_tag = consts.kUnifiedCurrencyTags[tier][stack_size]
            rule = self.GetRule(type_tag, tier_tag)
            if (currency_name in rule.GetBaseTypeList()):
                return tier
        logger.Log('Warning: currency "{}" not found in normal currency tiers'.format(
                           currency_name))
        return -1
    # End GetTierOfCurrency
    
    def GetAllCurrencyInTier(self, tier: int) -> List[str]:
        CheckType(tier, 'tier', int)
        if (not (1 <= tier <= consts.kNumCurrencyTiersExcludingScrolls)):
            logger.Log('Warning: currency tier {} is outside the valid currency tier range [{}, {}]'
                        .format(tier, 1, consts.kNumCurrencyTiersExcludingScrolls))
            return []
        stack_size = 1
        type_tag, tier_tag = consts.kUnifiedCurrencyTags[tier][stack_size]
        rule = self.GetRule(type_tag, tier_tag)
        return list(rule.GetBaseTypeList())  # returns a copy
    # End GetAllCurrencyInTier
    
    # Implementation function for SetCurrencyToTier - not part of public API.
    # Handles both stacked and unstacked currency.
    # Assumes consistency between stacked and unstacked currency tiers.
    def MoveCurrencyFromTierToTier(self, currency_name: str, original_tier: int, target_tier: int):
        CheckType(currency_name, 'currency_name', str)
        CheckType(original_tier, 'original_tier', int)
        CheckType(target_tier, 'target_tier', int)
        if (not (1 <= target_tier <= consts.kNumCurrencyTiersExcludingScrolls)):
            logger.Log(('Warning: currency "{}" could not be moved from tier {} to tier {}, '
                        'target tier is out of the valid currency tier range: [1, {}]').format(
                                currency_name, original_tier, target_tier,
                                consts.kNumCurrencyTiersExcludingScrolls))
            return
        # Remove currency_name from original_tier rule
        if (original_tier != -1):
            for stack_size in consts.kCurrencyStackSizesByTier[original_tier]:
                type_tag, tier_tag = consts.kUnifiedCurrencyTags[original_tier][stack_size]
                rule = self.GetRule(type_tag, tier_tag)
                rule.RemoveBaseType(currency_name)
        # Add currency_name to target_tier rule
        for stack_size in consts.kCurrencyStackSizesByTier[target_tier]:
            type_tag, tier_tag = consts.kUnifiedCurrencyTags[target_tier][stack_size]
            rule = self.GetRule(type_tag, tier_tag)
            rule.RemoveBaseType(currency_name)
            rule.AddBaseType(currency_name)
            rule.Enable()
    # End MoveCurrencyFromTierToTier
    
    def SetCurrencyTierMinVisibleStackSize(self, tier_param: str or int, min_stack_size_param: str or int):
        if (isinstance(tier_param, int)):
            tier_param = str(tier_param)
        if (isinstance(min_stack_size_param, int)):
            min_stack_size_param = str(min_stack_size_param)
        CheckType(tier_param, 'tier_param', str)
        CheckType(min_stack_size_param, 'min_stack_size_param', str)
        tier: int = consts.kCurrencyTierStringToIntMap[tier_param]
        min_stack_size: int = consts.kCurrencyStackSizeStringToIntMap[min_stack_size_param]
        # Check if min_stack_size is valid
        hide_all_sentinel = consts.kCurrencyStackSizeStringToIntMap['hide_all']
        valid_stack_sizes = consts.kCurrencyStackSizesByTier[tier] + [hide_all_sentinel]
        if (min_stack_size not in valid_stack_sizes):
            raise RuntimeError('min_stack_size {} invalid for tier {},'
                    'valid options are {}'.format(min_stack_size, tier, valid_stack_sizes))
        # Hide all stacks lower than stack_size, show all stacks greater than or equal to stack size
        for stack_size in consts.kCurrencyStackSizesByTier[tier]:
            type_tag, tier_tag = consts.kUnifiedCurrencyTags[tier][stack_size]
            rule = self.GetRule(type_tag, tier_tag)
            if (stack_size < min_stack_size):
                rule.Hide()
            else:
                rule.Show()
    # End SetCurrencyMinVisibleStackSize
    
    # Returns the min visible stack size for the given tier,
    # or the sentinel value (100, defined in consts.py) to indicate hide_all-
    def GetCurrencyTierMinVisibleStackSize(self, tier_param: str or int) -> int:
        if (isinstance(tier_param, int)):
            tier_param = str(tier_param)
        CheckType(tier_param, 'tier_param', str)
        tier: int = consts.kCurrencyTierStringToIntMap[tier_param]
        for stack_size in consts.kCurrencyStackSizesByTier[tier]:
            type_tag, tier_tag = consts.kUnifiedCurrencyTags[tier][stack_size]
            rule = self.GetRule(type_tag, tier_tag)
            if (rule.visibility == RuleVisibility.kShow):
                return stack_size
        # None are visible -> return hide_all sentinel
        return consts.kCurrencyStackSizeStringToIntMap['hide_all']
    # End GetCurrencyTierMinVisibleStackSize

    # ============================= Essence Functions =============================
    
    def SetEssenceTierVisibility(self, tier: int, visibility: RuleVisibility):
        CheckType(tier, 'tier', int)
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag, tier_tag = consts.kEssenceTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        rule.SetVisibility(visibility)
    # SetEssenceTierVisibility
    
    def GetEssenceTierVisibility(self, tier: int) -> RuleVisibility:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kEssenceTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        return rule.visibility
    # GetUniqueTierVisibility
    
    def SetHideEssencesAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kNumEssenceTiers + 1):
            visibility = (RuleVisibility.kHide if tier > max_visible_tier
                    else RuleVisibility.kShow)
            self.SetEssenceTierVisibility(tier, visibility)
    # SetHideEssencesAboveTierTier
    
    def GetHideEssencesAboveTierTier(self) -> int:
        # Iterate from highest to lowest tier
        for tier in range(consts.kNumEssenceTiers, 0, -1):
            if (self.GetEssenceTierVisibility(tier) == RuleVisibility.kShow):
                return tier
        # No tiers are visible
        return 0
    # GetHideEssencesAboveTierTier
    
    # ============================= Div Card Functions =============================
    
    def SetDivCardTierVisibility(self, tier: int, visibility: RuleVisibility):
        CheckType(tier, 'tier', int)
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag, tier_tag = consts.kDivCardTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        rule.SetVisibility(visibility)
    # SetDivCardTierVisibility
    
    def GetDivCardTierVisibility(self, tier: int) -> RuleVisibility:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kDivCardTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        return rule.visibility
    # GetDivCardTierVisibility
    
    def SetHideDivCardsAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kNumDivCardTiers + 1):
            visibility = (RuleVisibility.kHide if tier > max_visible_tier
                    else RuleVisibility.kShow)
            self.SetDivCardTierVisibility(tier, visibility)
    # SetHideDivCardsAboveTierTier
    
    def GetHideDivCardsAboveTierTier(self) -> int:
        # Iterate from highest to lowest tier
        for tier in range(consts.kNumDivCardTiers, 0, -1):
            if (self.GetDivCardTierVisibility(tier) == RuleVisibility.kShow):
                return tier
        # No tiers are visible
        return 0
    # GetHideDivCardsAboveTierTier
    
    # =========================== Unique Item Functions ===========================
    
    def SetUniqueItemTierVisibility(self, tier: int, visibility: RuleVisibility):
        CheckType(tier, 'tier', int)
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag, tier_tag = consts.kUniqueItemTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        rule.SetVisibility(visibility)
    # SetUniqueItemTierVisibility
    
    def GetUniqueItemTierVisibility(self, tier: int) -> RuleVisibility:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kUniqueItemTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        return rule.visibility
    # GetUniqueItemTierVisibility
    
    def SetHideUniqueItemsAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kNumUniqueItemTiers + 1):
            visibility = (RuleVisibility.kHide if tier > max_visible_tier
                    else RuleVisibility.kShow)
            self.SetUniqueItemTierVisibility(tier, visibility)
    # SetHideUniqueItemsAboveTierTier
    
    def GetHideUniqueItemsAboveTierTier(self) -> int:
        # Iterate from highest to lowest tier
        for tier in range(consts.kNumUniqueItemTiers, 0, -1):
            if (self.GetUniqueItemTierVisibility(tier) == RuleVisibility.kShow):
                return tier
        # No tiers are visible
        return 0
    # GetHideUniqueItemsAboveTierTier
    
    # ============================ Unique Map Functions ============================
    
    def SetUniqueMapTierVisibility(self, tier: int, visibility: RuleVisibility):
        CheckType(tier, 'tier', int)
        CheckType(visibility, 'visibility', RuleVisibility)
        type_tag, tier_tag = consts.kUniqueMapTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        rule.SetVisibility(visibility)
    # SetUniqueMapTierVisibility
    
    def GetUniqueMapTierVisibility(self, tier: int) -> RuleVisibility:
        CheckType(tier, 'tier', int)
        type_tag, tier_tag = consts.kUniqueMapTags[tier]
        rule = self.GetRule(type_tag, tier_tag)
        return rule.visibility
    # GetUniqueMapTierVisibility
    
    def SetHideUniqueMapsAboveTierTier(self, max_visible_tier: int):
        CheckType(max_visible_tier, 'max_visible_tier', int)
        for tier in range(1, consts.kNumUniqueMapTiers + 1):
            visibility = (RuleVisibility.kHide if tier > max_visible_tier
                    else RuleVisibility.kShow)
            self.SetUniqueMapTierVisibility(tier, visibility)
    # SetHideUniqueMapsAboveTierTier
    
    def GetHideUniqueMapsAboveTierTier(self) -> int:
        # Iterate from highest to lowest tier
        for tier in range(consts.kNumUniqueMapTiers, 0, -1):
            if (self.GetUniqueMapTierVisibility(tier) == RuleVisibility.kShow):
                return tier
        # No tiers are visible
        return 0
    # GetHideUniqueMapsAboveTierTier
    
    # =========================== Oil-Related Functions ===========================
    
    def SetLowestVisibleOil(self, lowest_visible_oil_name: str):
        type_tag = consts.kOilTypeTag
        visible_flag = True
        hide_rule = self.GetRule(type_tag, consts.kOilHideTierTag)
        for oil_name, tier in consts.kOilTierList:
            tier_tag = 't' + str(tier)
            rule = self.GetRule(type_tag, tier_tag)
            if (visible_flag):
                hide_rule.RemoveBaseType(oil_name)
                rule.AddBaseType(oil_name)
                rule.Enable()
            else:
                rule.RemoveBaseType(oil_name)
                hide_rule.AddBaseType(oil_name)
                hide_rule.Enable()
            if (oil_name == lowest_visible_oil_name):
                visible_flag = False  # hide rest below this oil
    # End SetLowestVisibleOil
    
    def GetLowestVisibleOil(self) -> str:
        type_tag = consts.kOilTypeTag
        # Iterate upwards from bottom oil to find first visible
        for oil_name, tier in reversed(consts.kOilTierList):
            tier_tag = 't' + str(tier)
            rule = self.GetRule(type_tag, tier_tag)
            if (oil_name in rule.GetBaseTypeList()):
                return oil_name
    # End GetLowestVisibleOil
    
    # ============================ Gem Quality Functions ============================
    
    # The rules we modify for gem quality functionality are:
    #  - Show # %D5 $type->gems-generic $tier->qt2   (19-20)
    #  - Show # %D3 $type->gems-generic $tier->qt3   (14-18)
    #  - Show # %D2 $type->gems-generic $tier->qt4   (1-13)
    def SetGemMinQuality(self, min_quality: int):
        CheckType(min_quality, 'min_quality', int)
        type_tag = consts.kQualityGemsTypeTag
        tier_tag_base = 'qt'
        quality_t2_rule = self.GetRule(type_tag, tier_tag_base + str(2))
        quality_t3_rule = self.GetRule(type_tag, tier_tag_base + str(3))
        quality_t4_rule = self.GetRule(type_tag, tier_tag_base + str(4))
        if (19 <= min_quality <= 20):
            quality_t2_rule.Show()
            quality_t2_rule.ModifyLine('Quality', '>=', min_quality)
            quality_t3_rule.Disable()
            quality_t4_rule.Disable()
        elif (14 <= min_quality <= 18):
            quality_t2_rule.Show()
            quality_t2_rule.ModifyLine('Quality', '>=', 19)
            quality_t3_rule.Show()
            quality_t3_rule.ModifyLine('Quality', '>=', min_quality)
            quality_t4_rule.Disable()
        elif (1 <= min_quality <= 13):
            quality_t2_rule.Show()
            quality_t2_rule.ModifyLine('Quality', '>=', 19)
            quality_t3_rule.Show()
            quality_t3_rule.ModifyLine('Quality', '>=', 14)
            quality_t4_rule.Show()
            quality_t4_rule.ModifyLine('Quality', '>=', min_quality)
    # End SetGemMinQuality
    
    def GetGemMinQuality(self):
        type_tag = consts.kQualityGemsTypeTag
        tier_tag_base = 'qt'
        for tier in [4, 3, 2, 1]:
            rule = self.GetRule(type_tag, tier_tag_base + str(tier))
            if (rule.visibility == RuleVisibility.kShow):
                op, [quality_string] = rule.parsed_lines_hll['Quality']
                return int(quality_string)
        return -1  # indicates all gem quality rules are disabled/hidden
    
    # ============================ Flask Quality Functions ============================
    
    # The rules we modify for flask quality functionality are:
    #  - Show # %D5 $type->endgameflasks $tier->qualityhigh  (14-20)
    #  - Show # %D3 $type->endgameflasks $tier->qualitylow   (1-13)
    # Note: any min_quality value outside the range [1, 20] will disable all flask quality rules
    def SetFlaskMinQuality(self, min_quality: int):
        CheckType(min_quality, 'min_quality', int)
        type_tag = consts.kQualityFlasksTypeTag
        quality_high_rule = self.GetRule(type_tag, 'qualityhigh')
        quality_low_rule = self.GetRule(type_tag, 'qualitylow')
        if (14 <= min_quality <= 20):
            quality_high_rule.Show()
            quality_high_rule.ModifyLine('Quality', '>=', min_quality)
            quality_low_rule.Disable()
        elif (1 <= min_quality <= 13):
            quality_high_rule.Show()
            quality_high_rule.ModifyLine('Quality', '>=', 14)
            quality_low_rule.Show()
            quality_low_rule.ModifyLine('Quality', '>=', min_quality)        
        else:  # out of range [1, 20] --> disable all flask quality rules
            quality_high_rule.Disable()
            quality_low_rule.Disable()
    # End SetFlaskMinQuality
    
    def GetFlaskMinQuality(self):
        type_tag = consts.kQualityFlasksTypeTag
        tier_tag_list = ['qualitylow', 'qualityhigh']
        for tier_tag in tier_tag_list:
            rule = self.GetRule(type_tag, tier_tag)
            if (rule.visibility == RuleVisibility.kShow):
                op, [quality_string] = rule.parsed_lines_hll['Quality']
                return int(quality_string)
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
                rule = self.GetRule(type_tag, tier_tag)
                if (size_int > max_size_int):
                    rule.Hide()
                else:
                    rule.Show()
    # End SetRgbItemMaxSize
    
    def GetRgbItemMaxSize(self) -> str:
        type_tag = consts.kRgbTypeTag
        max_size_string = 'none'
        max_size_int = 0
        # Iterating in a random order, so no early out
        for size_string, (size_int, tier_tag_list) in consts.kRgbSizesMap.items():
            for tier_tag in tier_tag_list:
                rule = self.GetRule(type_tag, tier_tag)
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
        rule = self.GetRule(type_tag, tier_tag)
        if (enable_flag):
            rule.Show()
        else:
            rule.Disable()
    # End IsChaosRecipeItemSlotEnabled
    
    def IsChaosRecipeEnabledFor(self, item_slot: str) -> bool:
        CheckType(item_slot, 'item_slot', str)
        if ((item_slot == 'Weapons') or (item_slot == 'weapons')):
            return self.IsChaosRecipeEnabledFor('WeaponsX')
        type_tag = consts.kChaosRecipeTypeTag
        tier_tag: str = (item_slot if item_slot in consts.kChaosRecipeTierTags.values()
                         else consts.kChaosRecipeTierTags[item_slot])
        rule = self.GetRule(type_tag, tier_tag)
        return rule.visibility == RuleVisibility.kShow
    # End IsChaosRecipeItemSlotEnabled
    
    # ======================== Private Parser Methods ========================
    
    def AddBlockToHll(self, block: List[str], successor_key=None):
        CheckType(block, 'block', list, str)
        if (len(block) == 0):
            return
        elif (LootFilterRule.IsParsableAsRule(block)):
            rule = LootFilterRule(block)
            key = rule.type_tag, rule.tier_tag
            if ((not rule.type_tag) or (not rule.tier_tag)):
                self.num_untagged_rules += 1
                rule.SetTypeTierTags(consts.kUntaggedRuleTypeTag, str(self.num_untagged_rules))
            self.rule_or_text_block_hll.insert_before(
                    key, RuleOrTextBlock(rule, is_rule=True), successor_key)
        else:  # not parsable as rule
            self.num_raw_text_blocks += 1
            key = kTextBlockKey, str(self.num_raw_text_blocks)
            self.rule_or_text_block_hll.insert_before(
                    key, RuleOrTextBlock(block, is_rule=False), successor_key)
    # End AddBlockToHll
    
    def ParseInputFilterFile(self) -> None:
        input_filter_fullpath = self.profile_obj.config_values[
                'OutputLootFilterFullpath'
                if (self.input_filter_source == InputFilterSource.kOutput)
                else 'InputLootFilterFullpath']
        if (not os.path.isfile(input_filter_fullpath)):
            raise RuntimeError('Input filter {} does not exist'.format(input_filter_fullpath))
        input_lines = file_helper.ReadFile(input_filter_fullpath, strip=True)
        # Break input lines into "blocks". A block is a group of consecutive lines
        # of text without any empty (whitespace-only) lines.
        # Each block will then be parsed into a RuleOrTextLines object.
        current_block = []
        for input_line in input_lines:
            if (input_line == ''):
                self.AddBlockToHll(current_block)
                current_block = []
            else:
                current_block.append(input_line)
        # Apply import changes if needed
        if (self.input_filter_source != InputFilterSource.kOutput):
            self.ApplyImportChanges()
    # End ParseLootFilterFile()
    
    # Returns the HllNode containing the Table of Contents block.
    # Raises an error if Table of Contents cannot be found.
    def FindTableOfContentsNode(self) -> HllNode:
        for key, rule_or_text_block in self.rule_or_text_block_hll:
            if (not rule_or_text_block.is_rule):
                text_lines = rule_or_text_block.text_lines
                toc_identifier = consts.kTableOfContentsIdentifier
                if (parse_helper.IsSubstringInLines(toc_identifier, text_lines)):
                    return self.rule_or_text_block_hll.get_node(key)
        raise RuntimeError('Table of Contents not found')
    # End FindTableOfContentsBlock

    def GenerateDlfRuleText(self) -> List[str]:
        text = ''
        current_section_id_int = int(consts.kDlfAddedRulesSectionGroupId)
        # Add section group header
        text += consts.kSectionGroupHeaderTemplate.format(current_section_id_int,
                consts.kDlfAddedRulesSectionGroupName) + '\n\n'
        # Add custom user-defined rules
        current_section_id_int += 1
        section_title_string = 'Custom rules from "{}"'.format(
                self.profile_obj.config_values['RulesFullpath'])
        text += consts.kSectionHeaderTemplate.format(
                current_section_id_int, section_title_string) + '\n\n'
        custom_rules_lines = file_helper.ReadFile(
                self.profile_obj.config_values['RulesFullpath'], strip=True)
        text += '\n'.join(custom_rules_lines) + '\n\n'
        # Add "Hide maps below tier" rule
        current_section_id_int += 1
        text += consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Hide all maps below specified tier') + '\n\n'
        text += consts.kHideMapsBelowTierRuleTemplate.format(
                self.profile_obj.config_values['HideMapsBelowTier']) + '\n\n'
        # Add BaseType rules
        current_section_id_int += 1
        text += consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Show specific BaseTypes') + '\n\n'
        text += consts.kBaseTypeRuleTemplateRare + '\n\n'
        text += consts.kBaseTypeRuleTemplateAny + '\n\n'
        # Add flask BaseType rules
        current_section_id_int += 1
        text += consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Show specific flask BaseTypes') + '\n\n'
        text += consts.kFlaskRuleTemplate + '\n\n'
        text += consts.kHighIlvlFlaskRuleTemplate + '\n\n'
        # Add chaos recipe rules
        current_section_id_int += 1
        text += consts.kSectionHeaderTemplate.format(
                current_section_id_int, 'Show chaos recipe rares by item slot') + '\n\n'
        # Weapons handled separately, since config tells us which classes to use
        item_slot = 'WeaponsX'
        weapon_classes = self.profile_obj.config_values['ChaosRecipeWeaponClassesAnyHeight']
        text += consts.GenerateChaosRecipeWeaponRule(item_slot, weapon_classes) + '\n\n'
        item_slot = 'Weapons3'
        weapon_classes = self.profile_obj.config_values['ChaosRecipeWeaponClassesMaxHeight3']
        text += consts.GenerateChaosRecipeWeaponRule(item_slot, weapon_classes) + '\n\n'
        # Handle the rest of chaos recipe rules
        for chaos_recipe_rule_string in consts.kChaosRecipeRuleStrings:
            text += chaos_recipe_rule_string + '\n\n'
        return text.split('\n')
    # End GenerateDlfRuleText

    # Insert the DLF rules immediately after the Table of Contents text block.
    def AddDlfRules(self):
        # If DLF HideMapsBelowTier rule already exists, return immediately.
        if (consts.kHideMapsBelowTierTags in self.rule_or_text_block_hll):
            return
        # Add DLF rules - very similar to ParseInputFilterFile code
        dlf_rule_text = self.GenerateDlfRuleText()
        successor_key = self.FindTableOfContentsNode().next_node.key
        current_block = []
        for line in dlf_rule_text:
            if (line == ''):
                self.AddBlockToHll(current_block, successor_key)
                current_block = []
            else:
                current_block.append(line)
    # End AddDlfRules
    
    # Standardizes all stacked currency tiers to their unstacked counterparts.
    # Called automatically on filter import.
    def StandardizeCurrencyTiers(self):
        for tier in range(1, consts.kNumCurrencyTiersExcludingScrolls + 1):
            unstacked_type_tag, unstacked_tier_tag = consts.kUnifiedCurrencyTags[tier][1]
            unstacked_rule = self.GetRule(unstacked_type_tag, unstacked_tier_tag)
            # Skip first (size 1) when iterating through stack sizes
            for stack_size in consts.kCurrencyStackSizesByTier[tier][1:]:
                stacked_type_tag, stacked_tier_tag = consts.kUnifiedCurrencyTags[tier][stack_size]
                stacked_rule = self.GetRule(stacked_type_tag, stacked_tier_tag)
                stacked_rule.ClearBaseTypeList()
                stacked_rule.AddBaseTypes(unstacked_rule.GetBaseTypeList())
                stacked_rule.Enable()
    # End StandarizeCurrencyTiers
    
    # Apply changes that need to be made to the filter on import only
    def ApplyImportChanges(self):
        # Add DLF header
        dlf_header_string = consts.kDlfHeaderTemplate.format(consts.kDlfVersion)
        dlf_header_rule_or_text_block = RuleOrTextBlock(
                dlf_header_string.split('\n'), is_rule=False)
        self.rule_or_text_block_hll.insert_at_index(
                consts.kDlfHeaderKey, dlf_header_rule_or_text_block, index=0)
        # Add DLF-generated rules and custom user rules
        self.AddDlfRules()
        # Make all stacked currency tiers match their unstacked counterparts
        self.StandardizeCurrencyTiers()
        # Set currency stack size thresholds to those defined in consts.kCurrencyStackSizes
        for tier, tag_pairs in consts.kStackedCurrencyTags.items():
            for i, (type_tag, tier_tag) in enumerate(tag_pairs):
                stack_size = consts.kCurrencyStackSizes[i + 1]
                rule = self.GetRule(type_tag, tier_tag)
                rule.ModifyLine('StackSize', '>=', stack_size)
        # Place oils in appropriate tiers
        oil_hide_rule = self.GetRule(consts.kOilTypeTag, consts.kOilHideTierTag)
        oil_hide_rule.Hide()
        oil_hide_rule.ClearBaseTypeList()  # disables the rule
        for oil_tier in range(1, consts.kMaxOilTier + 1):
            rule = self.GetRule(consts.kOilTypeTag, 't' + str(oil_tier))
            rule.ClearBaseTypeList()
        for oil_name, oil_tier in consts.kOilTierList:
            rule = self.GetRule(consts.kOilTypeTag, 't' + str(oil_tier))
            rule.AddBaseType(oil_name)
            rule.Show()
    # End ApplyImportChanges

# -----------------------------------------------------------------------------
