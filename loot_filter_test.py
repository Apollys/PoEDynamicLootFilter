from loot_filter import InputFilterSource, LootFilter
from loot_filter_rule import RuleVisibility

import filecmp

import consts
import file_helper
import os
import os.path
import parse_helper
import test_consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse, AssertFailure
import test_helper

def TestParseWriteFilter():
    test_helper.SetUp()
    # Parse downloaded filter
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    profile_config_values = loot_filter.profile_obj.config_values
    downloaded_filter_fullpath = test_consts.kTestProfileDownloadedFilterFullpath
    input_filter_fullpath = profile_config_values['InputLootFilterFullpath']
    output_filter_fullpath = profile_config_values['OutputLootFilterFullpath']
    # Check that downloaded filter was removed and input filter was created
    AssertFalse(os.path.isfile(downloaded_filter_fullpath))
    AssertTrue(os.path.isfile(input_filter_fullpath))
    # Verify that the input filter has the same contents as the source downloaded filter
    AssertTrue(filecmp.cmp(
            test_consts.kTestBaseFilterFullpath, input_filter_fullpath, shallow=False))
    # Write output filter
    loot_filter.SaveToFile()
    AssertTrue(os.path.isfile(output_filter_fullpath))
    # Check that written filter is longer than input filter (added DLF rules)
    num_input_filter_lines = file_helper.NumLines(input_filter_fullpath)
    num_output_filter_lines = file_helper.NumLines(output_filter_fullpath)
    AssertTrue(num_output_filter_lines - num_input_filter_lines > 20)
    print('TestParseWriteFilter passed!')

def TestMaps():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    # Apply change
    tier = 7
    loot_filter.SetHideMapsBelowTierTier(tier)
    # Verify result
    AssertEqual(loot_filter.GetHideMapsBelowTierTier(), tier)
    rule = loot_filter.GetRule(*consts.kHideMapsBelowTierTags)
    AssertEqual(rule.parsed_lines_hll['MapTier'], ('<', [str(tier)]))
    print('TestMaps passed!')

def TestGeneralBaseTypes():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    # Enable for any non-unique
    base_type = 'Sorcerer\'s Gloves'
    loot_filter.SetBaseTypeRuleEnabledFor(base_type, enable_flag=True, rare_only_flag=False)
    AssertTrue(loot_filter.IsBaseTypeRuleEnabledFor(base_type, rare_flag=False))
    AssertTrue(loot_filter.IsBaseTypeRuleEnabledFor(base_type, rare_flag=True))
    # Enable for rare only
    loot_filter.SetBaseTypeRuleEnabledFor(base_type, enable_flag=True, rare_only_flag=True)
    AssertFalse(loot_filter.IsBaseTypeRuleEnabledFor(base_type, rare_flag=False))
    AssertTrue(loot_filter.IsBaseTypeRuleEnabledFor(base_type, rare_flag=True))
    # Add another BaseType for any non-unique
    other_base_type = 'Driftwood Wand'
    loot_filter.SetBaseTypeRuleEnabledFor(other_base_type, enable_flag=True, rare_only_flag=False)
    # Verify GetAllVisibleBaseTypes is correct
    base_types_any = loot_filter.GetAllVisibleBaseTypes(rare_flag=False)
    base_types_rare = loot_filter.GetAllVisibleBaseTypes(rare_flag=True)
    AssertEqual(base_types_any, [other_base_type])
    AssertEqual(sorted(base_types_rare), sorted([base_type, other_base_type]))
    # Disable and verify
    loot_filter.SetBaseTypeRuleEnabledFor(base_type, enable_flag=False)
    AssertFalse(loot_filter.IsBaseTypeRuleEnabledFor(base_type, rare_flag=True))
    AssertFalse(loot_filter.IsBaseTypeRuleEnabledFor(base_type, rare_flag=False))
    AssertTrue(loot_filter.IsBaseTypeRuleEnabledFor(other_base_type, rare_flag=True))
    # Check rule directly
    type_tag = consts.kBaseTypeTypeTag
    tier_tag_rare = consts.kBaseTypeTierTagRare
    rule = loot_filter.GetRule(type_tag, tier_tag_rare)
    AssertTrue(other_base_type in rule.GetBaseTypeList())
    print('TestGeneralBaseTypes passed!')

def TestFlaskBaseTypes():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    # First, non high ilvl flask
    # Enable
    flask_base_type = 'Quicksilver Flask'
    loot_filter.SetFlaskRuleEnabledFor(flask_base_type, enable_flag=True, high_ilvl_flag=False)
    # Verify result
    AssertTrue(loot_filter.IsFlaskRuleEnabledFor(flask_base_type, high_ilvl_flag=False))
    AssertFalse(loot_filter.IsFlaskRuleEnabledFor(flask_base_type, high_ilvl_flag=True))
    AssertFalse(loot_filter.IsFlaskRuleEnabledFor('Other Flask', high_ilvl_flag=False))
    type_tag, tier_tag = 'dlf_flasks', 'dlf_flasks'
    rule = loot_filter.GetRule(type_tag, tier_tag)
    AssertTrue(flask_base_type in rule.GetBaseTypeList())
    # Disable and verify
    loot_filter.SetFlaskRuleEnabledFor(flask_base_type, enable_flag=False, high_ilvl_flag=False)
    AssertFalse(loot_filter.IsFlaskRuleEnabledFor(flask_base_type, high_ilvl_flag=False))
    rule = loot_filter.GetRule(type_tag, tier_tag)
    AssertFalse(flask_base_type in rule.GetBaseTypeList())
    # Second, high ilvl flask
    flask_base_type = 'Diamond Flask'
    loot_filter.SetFlaskRuleEnabledFor(flask_base_type, enable_flag=True, high_ilvl_flag=True)
    AssertTrue(loot_filter.IsFlaskRuleEnabledFor(flask_base_type, high_ilvl_flag=True))
    tier_tag = 'dlf_flasks_high_ilvl'
    rule = loot_filter.GetRule(type_tag, tier_tag)
    AssertTrue(flask_base_type in rule.GetBaseTypeList())
    print('TestFlaskBaseTypes passed!')

def TestAddDlfHeader():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    loot_filter.SaveToFile()
    output_filter_fullpath = loot_filter.profile_obj.config_values['OutputLootFilterFullpath']
    loot_filter_lines = file_helper.ReadFile(output_filter_fullpath)
    dlf_header_identifier = 'This filter has been modified by Dynamic Loot Filter version '
    found_dlf_header_flag = False
    for line in loot_filter_lines:
        if (dlf_header_identifier in line):
            found_dlf_header_flag = True
            break
    AssertTrue(found_dlf_header_flag)
    print('TestAddDlfHeader passed!')

# Handpicked examples of currency with mismatched tiers in input filter (NeversinkStrict):
#  - Chromatic Orb: unstacked T7, stacked T5
#  - Chaos Orb: unstacked T4, stackedsix T2, stackedthree T3
#  - Transmutation Shard: unstacked T9, not present in stacked
# Note: Stacked currency rules go up to T7; T8 = stackedsupplieshigh, T9 = stackedsupplieslow
def TestStandardizeCurrencyTiers():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    # Chromatic Orb
    currency_base_type = 'Chromatic Orb'
    unstacked_tier = 7
    AssertEqual(loot_filter.GetTierOfCurrency(currency_base_type), unstacked_tier)
    for stack_size, tags in consts.kUnifiedCurrencyTags[unstacked_tier].items():
        rule = loot_filter.GetRule(*tags)
        AssertTrue(currency_base_type in rule.GetBaseTypeList())
    # Chaos Orb
    currency_base_type = 'Chaos Orb'
    unstacked_tier = 4
    AssertEqual(loot_filter.GetTierOfCurrency(currency_base_type), unstacked_tier)
    for stack_size, tags in consts.kUnifiedCurrencyTags[unstacked_tier].items():
        rule = loot_filter.GetRule(*tags)
        AssertTrue(currency_base_type in rule.GetBaseTypeList())
    # Transmutation Shard
    currency_base_type = 'Transmutation Shard'
    unstacked_tier = 9
    AssertEqual(loot_filter.GetTierOfCurrency(currency_base_type), unstacked_tier)
    for stack_size, tags in consts.kUnifiedCurrencyTags[unstacked_tier].items():
        rule = loot_filter.GetRule(*tags)
        AssertTrue(currency_base_type in rule.GetBaseTypeList())
    print('TestStandardizeCurrencyTiers passed!')

# After import, stack size thresholds should match those defined in consts.kCurrencyStackSizesByTier
def TestApplyDlfCurrencyStackSizes():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for tier, stack_sizes in consts.kCurrencyStackSizesByTier.items():
        for stack_size in stack_sizes:
            if (stack_size == 1): continue
            tags = consts.kUnifiedCurrencyTags[tier][stack_size]
            rule = loot_filter.GetRule(*tags)
            AssertEqual(rule.parsed_lines_hll['StackSize'], ('>=', [str(stack_size)]))
    print('TestApplyDlfCurrencyStackSizes passed!')

kT1CurrencyBaseTypes = '''"Albino Rhoa Feather" "Awakener's Orb" "Crusader's Exalted Orb" "Eternal Orb" "Exalted Orb" "Hunter's Exalted Orb" "Mirror of Kalandra" "Mirror Shard" "Orb of Dominance" "Prime Regrading Lens" "Redeemer's Exalted Orb" "Secondary Regrading Lens" "Tailoring Orb" "Tainted Divine Teardrop" "Tempering Orb" "Warlord's Exalted Orb"'''
kT1CurrencyBaseTypeList = parse_helper.ConvertValuesStringToList(kT1CurrencyBaseTypes)

def TestCurrencyTiers():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    # Test GetAllCurrencyInTier
    get_t1_currency_result = loot_filter.GetAllCurrencyInTier(1)
    AssertEqual(sorted(get_t1_currency_result), sorted(kT1CurrencyBaseTypeList))
    # Test SetCurrencyToTier/GetTierOfCurrency
    currency_base_type = 'Chromatic Orb'
    initial_tier = loot_filter.GetTierOfCurrency(currency_base_type)
    target_tier = ((initial_tier + 4) % consts.kNumCurrencyTiersExcludingScrolls) + 1
    # Set currency to target tier
    loot_filter.SetCurrencyToTier(currency_base_type, target_tier)
    AssertEqual(loot_filter.GetTierOfCurrency(currency_base_type), target_tier)
    # Verify rule text for new tier contains base type
    for stack_size, tags in consts.kUnifiedCurrencyTags[target_tier].items():
        rule = loot_filter.GetRule(*tags)
        AssertTrue(currency_base_type in rule.GetBaseTypeList())
    # Verify initial rule no longer contains base type
    for stack_size, tags in consts.kUnifiedCurrencyTags[initial_tier].items():
        rule = loot_filter.GetRule(*tags)
        AssertFalse(currency_base_type in rule.GetBaseTypeList())
    print('TestCurrencyTiers passed!')

def TestCurrencyStackSizeVisibility():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    tier = 6
    min_visible_stack_size = 4
    loot_filter.SetCurrencyTierMinVisibleStackSize(tier, min_visible_stack_size)
    AssertEqual(loot_filter.GetCurrencyTierMinVisibleStackSize(tier), min_visible_stack_size)
    # Check rules have correct Show/Hide status
    for stack_size, tags in consts.kUnifiedCurrencyTags[tier].items():
        rule = loot_filter.GetRule(*tags)
        if (stack_size < min_visible_stack_size):
            AssertEqual(rule.visibility, RuleVisibility.kHide)
        else:
            AssertEqual(rule.visibility, RuleVisibility.kShow)
    # Test hide_all
    loot_filter.SetCurrencyTierMinVisibleStackSize(tier, 'hide_all')
    AssertEqual(loot_filter.GetCurrencyTierMinVisibleStackSize(tier),
            consts.kCurrencyStackSizeStringToIntMap['hide_all'])
    print('TestCurrencyStackSizeVisibility passed!')

def TestEssences():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for max_visible_tier in [2, 0]:
        loot_filter.SetHideEssencesAboveTierTier(max_visible_tier)
        AssertEqual(loot_filter.GetHideEssencesAboveTierTier(), max_visible_tier)
        for tier, tags in consts.kEssenceTags.items():
            rule = loot_filter.GetRule(*tags)
            if (tier > max_visible_tier):
                AssertEqual(loot_filter.GetEssenceTierVisibility(tier), RuleVisibility.kHide)
                AssertEqual(rule.visibility, RuleVisibility.kHide)
            else:
                AssertEqual(loot_filter.GetEssenceTierVisibility(tier), RuleVisibility.kShow)
                AssertEqual(rule.visibility, RuleVisibility.kShow)
    print('TestEssences passed!')

# Same functionality as Essences, only tags and function names are different
def TestDivCards():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for max_visible_tier in [2, 0]:
        loot_filter.SetHideDivCardsAboveTierTier(max_visible_tier)
        AssertEqual(loot_filter.GetHideDivCardsAboveTierTier(), max_visible_tier)
        for tier, tags in consts.kDivCardTags.items():
            rule = loot_filter.GetRule(*tags)
            if (tier > max_visible_tier):
                AssertEqual(loot_filter.GetDivCardTierVisibility(tier), RuleVisibility.kHide)
                AssertEqual(rule.visibility, RuleVisibility.kHide)
            else:
                AssertEqual(loot_filter.GetDivCardTierVisibility(tier), RuleVisibility.kShow)
                AssertEqual(rule.visibility, RuleVisibility.kShow)
    print('TestDivCards passed!')

# Same functionality as Essences, only tags and function names are different
def TestUniqueItems():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for max_visible_tier in [2, 0]:
        loot_filter.SetHideUniqueItemsAboveTierTier(max_visible_tier)
        AssertEqual(loot_filter.GetHideUniqueItemsAboveTierTier(), max_visible_tier)
        for tier, tags in consts.kUniqueItemTags.items():
            rule = loot_filter.GetRule(*tags)
            if (tier > max_visible_tier):
                AssertEqual(loot_filter.GetUniqueItemTierVisibility(tier), RuleVisibility.kHide)
                AssertEqual(rule.visibility, RuleVisibility.kHide)
            else:
                AssertEqual(loot_filter.GetUniqueItemTierVisibility(tier), RuleVisibility.kShow)
                AssertEqual(rule.visibility, RuleVisibility.kShow)
    print('TestUniqueItems passed!')

# Same functionality as Essences, only tags and function names are different
def TestUniqueMaps():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for max_visible_tier in [2, 0]:
        loot_filter.SetHideUniqueMapsAboveTierTier(max_visible_tier)
        AssertEqual(loot_filter.GetHideUniqueMapsAboveTierTier(), max_visible_tier)
        for tier, tags in consts.kUniqueMapTags.items():
            rule = loot_filter.GetRule(*tags)
            if (tier > max_visible_tier):
                AssertEqual(loot_filter.GetUniqueMapTierVisibility(tier), RuleVisibility.kHide)
                AssertEqual(rule.visibility, RuleVisibility.kHide)
            else:
                AssertEqual(loot_filter.GetUniqueMapTierVisibility(tier), RuleVisibility.kShow)
                AssertEqual(rule.visibility, RuleVisibility.kShow)
    print('TestUniqueMaps passed!')

def TestOils():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for lowest_visible_oil in ['Azure Oil', 'Clear Oil', 'Tainted Oil']:
        loot_filter.SetLowestVisibleOil(lowest_visible_oil)
        AssertEqual(loot_filter.GetLowestVisibleOil(), lowest_visible_oil)
        visible_flag = True
        # Check oil is in the correct rule
        for oil_name, tier in consts.kOilTierList:
            # If visible, it should be in the rule associated with `tier`
            if (visible_flag):
                rule = loot_filter.GetRule(consts.kOilTypeTag, 't{}'.format(tier))
                AssertTrue(oil_name in rule.GetBaseTypeList())
                AssertEqual(rule.visibility, RuleVisibility.kShow)
            # Otherwise, it should be in the hide tier
            else:
                rule = loot_filter.GetRule(consts.kOilTypeTag, consts.kOilHideTierTag)
                AssertTrue(oil_name in rule.GetBaseTypeList())
                AssertEqual(rule.visibility, RuleVisibility.kHide)
            # If found lowest_visible_oil, all subsequence oils should be hidden
            if (oil_name == lowest_visible_oil):
                visible_flag = False
    print('TestOils passed!')

def TestQualityGems():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for gem_min_quality in [1, 10, 15, 20]:
        loot_filter.SetGemMinQuality(gem_min_quality)
        AssertEqual(loot_filter.GetGemMinQuality(), gem_min_quality)
    # Check the appropriate rules are updated correctly for a specific quality value.
    # For gem_min_quality = 17, we should have:
    #  - qt2 = Show, Quality >= 19
    #  - qt3 = Show, Quality >= 17
    #  - qt4 = Disabled
    gem_min_quality = 17
    loot_filter.SetGemMinQuality(gem_min_quality)
    AssertEqual(loot_filter.GetGemMinQuality(), gem_min_quality)
    type_tag = consts.kQualityGemsTypeTag
    qt2_rule = loot_filter.GetRule(type_tag, 'qt2')
    qt3_rule = loot_filter.GetRule(type_tag, 'qt3')
    qt4_rule = loot_filter.GetRule(type_tag, 'qt4')
    AssertEqual(qt2_rule.visibility, RuleVisibility.kShow)
    AssertEqual(qt2_rule.parsed_lines_hll['Quality'], ('>=', ['19']))
    AssertEqual(qt3_rule.visibility, RuleVisibility.kShow)
    AssertEqual(qt3_rule.parsed_lines_hll['Quality'], ('>=', [str(gem_min_quality)]))
    AssertTrue(RuleVisibility.IsDisabled(qt4_rule.visibility))
    print('TestQualityGems passed!')

# Similar to quality gems, but one fewer tiers
def TestQualityFlasks():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for flask_min_quality in [1, 9, 18, 20]:
        loot_filter.SetFlaskMinQuality(flask_min_quality)
        AssertEqual(loot_filter.GetFlaskMinQuality(), flask_min_quality)
    # Check the appropriate rules are updated correctly for a specific quality value.
    # For flask_min_quality = 16, we should have:
    #  - qualityhigh = Show, Quality >= 16
    #  - qualitylow = Disabled
    flask_min_quality = 16
    loot_filter.SetFlaskMinQuality(flask_min_quality)
    AssertEqual(loot_filter.GetFlaskMinQuality(), flask_min_quality)
    type_tag = consts.kQualityFlasksTypeTag
    qualityhigh_rule = loot_filter.GetRule(type_tag, 'qualityhigh')
    qualitylow_rule = loot_filter.GetRule(type_tag, 'qualitylow')
    AssertEqual(qualityhigh_rule.visibility, RuleVisibility.kShow)
    AssertEqual(qualityhigh_rule.parsed_lines_hll['Quality'], ('>=', [str(flask_min_quality)]))
    AssertTrue(RuleVisibility.IsDisabled(qualitylow_rule.visibility))
    print('TestQualityFlasks passed!')

def TestRgbItems():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    for max_size_string in ['medium', 'large', 'small', 'none']:
        loot_filter.SetRgbItemMaxSize(max_size_string)
        AssertEqual(loot_filter.GetRgbItemMaxSize(), max_size_string)
    # Check the appropriate rules are updated correctly for a specific max_size_string value.
    # For max_size_string = 'small', we should have:
    #  - 'rgbsmall1', 'rgbsmall2' -> Show
    #  - 'rgbmedium', 'rgblarge' -> Hide
    # (Hide rather than Disable because it still applies style, and FilterBlade does it that way.)
    max_size_string = 'small'
    loot_filter.SetRgbItemMaxSize(max_size_string)
    AssertEqual(loot_filter.GetRgbItemMaxSize(), max_size_string)
    type_tag = consts.kRgbTypeTag
    show_tier_tags = ['rgbsmall1', 'rgbsmall2']
    hide_tier_tags = ['rgbmedium', 'rgblarge']
    for tier_tag in show_tier_tags:
        rule = loot_filter.GetRule(type_tag, tier_tag)
        AssertEqual(rule.visibility, RuleVisibility.kShow)
    for tier_tag in hide_tier_tags:
        rule = loot_filter.GetRule(type_tag, tier_tag)
        AssertEqual(rule.visibility, RuleVisibility.kHide)
    print('TestRgbItems passed!')

def TestChaosRecipeItems():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    type_tag = consts.kChaosRecipeTypeTag
    enable_flag = True
    for item_slot in consts.kChaosRecipeItemSlots:
        enable_flag = not enable_flag  # alternate enable/disable
        loot_filter.SetChaosRecipeEnabledFor(item_slot, enable_flag)
        AssertEqual(loot_filter.IsChaosRecipeEnabledFor(item_slot), enable_flag)
        rules = []
        if (item_slot in consts.kChaosRecipeTierTags):  # non-weapons
            tier_tag = consts.kChaosRecipeTierTags[item_slot]
            rules.append(loot_filter.GetRule(type_tag, tier_tag))
        else:  # weapons
            AssertTrue(item_slot == 'Weapons')
            for tier_tag in ['weapons_any_height', 'weapons_max_height_3']:
                rules.append(loot_filter.GetRule(type_tag, tier_tag))
        for rule in rules:
            if (enable_flag):
                AssertEqual(rule.visibility, RuleVisibility.kShow)
            else:
                AssertTrue(RuleVisibility.IsDisabled(rule.visibility))
    print('TestChaosRecipeItems passed!')

def TestImportNonFilterBladeFilter():
    test_helper.SetUp(profile_config_values=test_consts.kTestNonFilterBladeProfileConfigValues)
    # Check that we get a helpful error message when parsing the filter
    try:
        loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    except RuntimeError as e:
        AssertTrue('does not appear to be a FilterBlade filter' in repr(e))
    else:
        AssertFailure()
    print('TestImportNonFilterBladeFilter passed!')

def main():
    TestParseWriteFilter()
    TestMaps()
    TestGeneralBaseTypes()
    TestFlaskBaseTypes()
    TestAddDlfHeader()
    TestStandardizeCurrencyTiers()
    TestApplyDlfCurrencyStackSizes()
    TestCurrencyTiers()
    TestCurrencyStackSizeVisibility()
    TestEssences()
    TestDivCards()
    TestUniqueItems()
    TestUniqueMaps()
    TestQualityGems()
    TestOils()
    TestQualityFlasks()
    TestRgbItems()
    TestChaosRecipeItems()
    TestImportNonFilterBladeFilter()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()