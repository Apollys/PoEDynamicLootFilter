import os  # subprocess.run creating all sorts of problems, so we use os.system
import os.path
import random
import shutil

from backend_cli import kInputFilename as kBackendCliInputFilename
from backend_cli import kOutputFilename as kBackendCliOutputFilename
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
import profile
from type_checker import CheckType

kPythonCommand = 'python'
kTestLogFilename = 'test.log'
kTestProfileName = 'TestProfile'

kTestProfileConfigString = \
'''# Profile config file for profile: "TestProfile"

# Loot filter file locations
Download directory: FiltersDownload
Input (backup) loot filter directory: FiltersInput
Path of Exile directory: FiltersPathOfExile
Downloaded loot filter filename: NeversinkSemiStrict.filter
Output (Path of Exile) loot filter filename: TestDynamicLootFilter.filter

# Remove filter from downloads directory when importing?
# Filter will still be saved in Input directory even if this is True
Remove downloaded filter: False

# Loot filter options
Hide maps below tier: 0
Add chaos recipe rules: True
Chaos recipe weapon classes, any height: Daggers, Rune Daggers, Wands
Chaos recipe weapon classes, max height 3: Bows
'''

def CHECK(expr: bool):
    if (not expr):
        raise RuntimeError('CHECK failed: expression evaluated to False')
# End CHECK

def CheckOutput(expected_output_string: str):
    CheckType(expected_output_string, 'expected_output_string', str)
    output_string = ''.join(helper.ReadFile(kBackendCliOutputFilename))
    if (output_string.strip() != expected_output_string.strip()):
        raise RuntimeError('CheckOutput failed: expected "{}", got "{}"'.format(
                expected_output_string, output_string))
# End CheckOutput

# Parses the backend cli output file into a dict, where each line represents an item
# Lines are assumed to be of the form <key>;<value>, value is parsed as the given value_type
def ParseOutputAsDict(value_type: type):
    CheckType(value_type, 'value_type', type)
    split_lines = [line.split(';') for line in helper.ReadFile(kBackendCliOutputFilename)]
    return {split_line[0] : value_type(split_line[1]) for split_line in split_lines}
# End ParseOutputAsDict

def ResetTestProfile():
    # Write config string to config file
    helper.WriteToFile(
            kTestProfileConfigString, profile.GetProfileConfigFullpath(kTestProfileName))
    # Clear rules and changes fules
    open(profile.GetProfileRulesFullpath(kTestProfileName), 'w').close()
    open(profile.GetProfileChangesFullpath(kTestProfileName), 'w').close()
# End ResetTestProfile

# Input is the backend_cli function and optional parameters - TestProfile will be added
# Example: 'set_currency_tier "Chromatic Orb" 5'
def CallCliFunction(function_call: str):
    CheckType(function_call, 'function_call', str)
    full_command: str = kPythonCommand + ' backend_cli.py ' + function_call + ' ' + kTestProfileName
    return_value = os.system(full_command)
    CHECK(return_value == 0)
# End RunCommand

def TestSetRuleVisibility():
    print('Running TestSetRuleVisibility...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    type_tag, tier_tag = consts.kUnifiedCurrencyTags[1][1]
    # Test "hide"
    CallCliFunction('set_rule_visibility {} {} hide'.format(type_tag, tier_tag))
    loot_filter = LootFilter(kTestProfileName, output_as_input_filter = True)
    rule = loot_filter.GetRuleByTypeTier(type_tag, tier_tag)
    CHECK(rule.visibility == RuleVisibility.kHide)
    # Test "disable"
    CallCliFunction('set_rule_visibility {} {} disable'.format(type_tag, tier_tag))
    loot_filter = LootFilter(kTestProfileName, output_as_input_filter = True)
    rule = loot_filter.GetRuleByTypeTier(type_tag, tier_tag)
    CHECK(rule.visibility == RuleVisibility.kDisable)
    CHECK(all(line.startswith('#') for line in rule.text_lines))
    # Test "show"
    CallCliFunction('set_rule_visibility {} {} show'.format(type_tag, tier_tag))
    loot_filter = LootFilter(kTestProfileName, output_as_input_filter = True)
    rule = loot_filter.GetRuleByTypeTier(type_tag, tier_tag)
    CHECK(rule.visibility == RuleVisibility.kShow)
# End TestChangeRuleVisibility

def TestCurrency():
    print('Running TestCurrency...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    # Get and parse all currency tiers
    CallCliFunction('get_all_currency_tiers')
    currency_to_tier_map = ParseOutputAsDict(value_type = int)
    tier_to_currency_map = {}
    for currency_name, tier in currency_to_tier_map.items():
        if (tier not in tier_to_currency_map):
            tier_to_currency_map[tier] = []
        tier_to_currency_map[tier].append(currency_name)
    # Test set_currency_tier, adjust_currency_tier, and get_currency_tier
    max_tier = consts.kNumCurrencyTiersExcludingScrolls
    for original_tier in [1, random.randint(2, max_tier - 1), max_tier]:
        # Test set_currency_tier
        currency_name = random.choice(tier_to_currency_map[original_tier])
        target_tier = random.randint(1, max_tier)
        CallCliFunction('set_currency_to_tier "{}" {}'.format(currency_name, target_tier))
        CallCliFunction('get_tier_of_currency "{}"'.format(currency_name))
        CheckOutput(str(target_tier))
        # Reset currency to original tier for future tests
        CallCliFunction('set_currency_to_tier "{}" {}'.format(currency_name, original_tier))
    # Test set_/get_currency_tier_min_visible_stack_size
    test_tier_strings = [str(random.randint(1, max_tier)), 'tportal']
    for tier_str in test_tier_strings:
        tier_int = consts.kCurrencyTierStringToIntMap[tier_str]
        min_visible_stack_size = random.choice(consts.kCurrencyStackSizesByTier[tier_int])
        CallCliFunction('set_currency_tier_min_visible_stack_size {} {}'.format(
                tier_str, min_visible_stack_size))
        CallCliFunction('get_currency_tier_min_visible_stack_size {}'.format(tier_str))
        CheckOutput(str(min_visible_stack_size))
# End TestCurrency

def TestEssences():
    print('Running TestEssences...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    kNumTiers = consts.kNumEssenceTiers
    for max_visible_tier in [1, random.randint(2, kNumTiers - 1), kNumTiers]:
        CallCliFunction('set_hide_essences_above_tier {}'.format(max_visible_tier))
        CallCliFunction('get_hide_essences_above_tier')
        CheckOutput(str(max_visible_tier))
        CallCliFunction('get_all_essence_tier_visibilities')
        expected_output_string = '\n'.join('{};{}'.format(tier, int(tier <= max_visible_tier))
                for tier in range(1, kNumTiers + 1))
        CheckOutput(expected_output_string)
# End TestEssences

def TestDivCards():
    print('Running TestDivCards...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    kNumTiers = consts.kNumDivCardTiers
    for max_visible_tier in [1, random.randint(2, kNumTiers - 1), kNumTiers]:
        CallCliFunction('set_hide_div_cards_above_tier {}'.format(max_visible_tier))
        CallCliFunction('get_hide_div_cards_above_tier')
        CheckOutput(str(max_visible_tier))
        CallCliFunction('get_all_div_card_tier_visibilities')
        expected_output_string = '\n'.join('{};{}'.format(tier, int(tier <= max_visible_tier))
                for tier in range(1, kNumTiers + 1))
        CheckOutput(expected_output_string)
# End TestDivCards

def TestUniqueItems():
    print('Running TestUniqueItems...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    kNumTiers = consts.kNumUniqueItemTiers
    for max_visible_tier in [1, random.randint(2, kNumTiers - 1), kNumTiers]:
        CallCliFunction('set_hide_unique_items_above_tier {}'.format(max_visible_tier))
        CallCliFunction('get_hide_unique_items_above_tier')
        CheckOutput(str(max_visible_tier))
        CallCliFunction('get_all_unique_item_tier_visibilities')
        expected_output_string = '\n'.join('{};{}'.format(tier, int(tier <= max_visible_tier))
                for tier in range(1, kNumTiers + 1))
        CheckOutput(expected_output_string)
# End TestUniqueItems

def TestUniqueMaps():
    print('Running TestUniqueMaps...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    kNumTiers = consts.kNumUniqueMapTiers
    for max_visible_tier in [1, random.randint(2, kNumTiers - 1), kNumTiers]:
        CallCliFunction('set_hide_unique_maps_above_tier {}'.format(max_visible_tier))
        CallCliFunction('get_hide_unique_maps_above_tier')
        CheckOutput(str(max_visible_tier))
        CallCliFunction('get_all_unique_map_tier_visibilities')
        expected_output_string = '\n'.join('{};{}'.format(tier, int(tier <= max_visible_tier))
                for tier in range(1, kNumTiers + 1))
        CheckOutput(expected_output_string)
# End TestUniqueMaps

def TestOils():
    print('Running TestOils...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    oil_tier_names_map = {tier : [] for tier in range(1, consts.kMaxOilTier + 1)}
    for oil_name, tier in consts.kOilTierList:
        oil_tier_names_map[tier].append(oil_name)
    for tier in range(1, consts.kMaxOilTier + 1):
        lowest_visible_oil_name = random.choice(oil_tier_names_map[tier])
        CallCliFunction('set_lowest_visible_oil "{}"'.format(lowest_visible_oil_name))
        CallCliFunction('get_lowest_visible_oil')
        CheckOutput(lowest_visible_oil_name)
# End TestOils

def TestGemQuality():
    print('Running TestGemQuality...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    for min_visible_quality in [1, random.randint(2, 13), random.randint(14, 18), 19, 20]:
        CallCliFunction('set_gem_min_quality {}'.format(min_visible_quality))
        CallCliFunction('get_gem_min_quality')
        CheckOutput(str(min_visible_quality))
# End TestGemQuality

def TestFlaskQuality():
    print('Running TestFlaskQuality...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    for min_visible_quality in [1, random.randint(2, 13), 14, random.randint(15, 19), 20]:
        CallCliFunction('set_flask_min_quality {}'.format(min_visible_quality))
        CallCliFunction('get_flask_min_quality')
        CheckOutput(str(min_visible_quality))
# End TestFlaskQuality

def TestHideMapsBelowTier():
    print('Running TestHideMapsBelowTier...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    # Initial value is 0 for test profile
    CallCliFunction('get_hide_maps_below_tier')
    CheckOutput('0')
    for i in range(3):
        tier = random.randint(0, 16)
        CallCliFunction('set_hide_maps_below_tier {}'.format(tier))
        CallCliFunction('get_hide_maps_below_tier')
        CheckOutput(str(tier))
# End TestHideMapsBelowTier

def TestFlasks():
    print('Running TestFlasks...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    CallCliFunction('get_all_flask_visibilities')
    flask_visibility_map = ParseOutputAsDict(value_type = int)
    flask_type_list = list(flask_visibility_map.keys())
    for i in range(3):
        flask_type = random.choice(flask_type_list)
        original_visibility_flag = flask_visibility_map[flask_type]
        CallCliFunction('get_flask_visibility "{}"'.format(flask_type))
        CheckOutput(str(original_visibility_flag) + ' 0')  # we're not yet testing high ilvl
        desired_visibility_flag = random.randint(0, 1)
        CallCliFunction('set_flask_visibility "{}" {}'.format(flask_type, desired_visibility_flag))
        CallCliFunction('get_flask_visibility "{}"'.format(flask_type))
        CheckOutput(str(desired_visibility_flag) + ' 0')  # we're not yet testing high ilvl
        flask_visibility_map[flask_type] = desired_visibility_flag
# End TestFlasks

def TestRgbItems():
    print('Running TestRgbItems...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    for target_max_size_string in consts.kRgbSizesMap:
        CallCliFunction('set_rgb_item_max_size {}'.format(target_max_size_string))
        CallCliFunction('get_rgb_item_max_size')
        CheckOutput(target_max_size_string)
        # Parse the loot filter and check if the rules have correct visibilities
        loot_filter = LootFilter(kTestProfileName, output_as_input_filter = True)
        type_tag = consts.kRgbTypeTag
        target_max_size_int, _ = consts.kRgbSizesMap[target_max_size_string]
        for size_string, (size_int, tier_tag_list) in consts.kRgbSizesMap.items():
            for tier_tag in tier_tag_list:
                rule = loot_filter.GetRuleByTypeTier(type_tag, tier_tag)
                expected_visibility = (RuleVisibility.kShow if size_int <= target_max_size_int
                                       else RuleVisibility.kHide)
                CHECK(rule.visibility == expected_visibility)
# End TestRgbItems
    
def TestChaosRecipe():
    print('Running TestChaosRecipe...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    CallCliFunction('get_all_chaos_recipe_statuses')
    original_enabled_status_map = ParseOutputAsDict(value_type = int)
    desired_enabled_status_map = {
            item_slot : random.randint(0, 1) for item_slot in original_enabled_status_map}
    for item_slot, original_enabled_status in original_enabled_status_map.items():
        CallCliFunction('is_chaos_recipe_enabled_for "{}"'.format(item_slot))
        CheckOutput(str(original_enabled_status))
        CallCliFunction('set_chaos_recipe_enabled_for "{}" {}'.format(
                item_slot, desired_enabled_status_map[item_slot]))
    for item_slot, desired_enabled_status in desired_enabled_status_map.items():
        CallCliFunction('is_chaos_recipe_enabled_for "{}"'.format(item_slot))
        CheckOutput(str(desired_enabled_status))
# End TestChaosRecipe

kTestBatchString = \
'''get_all_currency_tiers
set_currency_to_tier "Chromatic Orb" 3
set_currency_to_tier "Chromatic Orb" 2
get_tier_of_currency "Chromatic Orb"
set_currency_tier_min_visible_stack_size 2 4
get_currency_tier_min_visible_stack_size 2
set_currency_tier_min_visible_stack_size twisdom 1
get_currency_tier_min_visible_stack_size twisdom
get_all_unique_item_tier_visibilities
set_hide_unique_items_above_tier 1
get_hide_unique_items_above_tier
set_gem_min_quality 18
get_gem_min_quality
set_hide_maps_below_tier 13
get_hide_maps_below_tier
get_all_flask_visibilities
set_flask_visibility "Quicksilver Flask" 1
set_flask_visibility "Gold Flask" 0
get_flask_visibility "Quicksilver Flask"
get_flask_visibility "Gold Flask"
set_chaos_recipe_enabled_for "Weapons" 0
set_chaos_recipe_enabled_for "Body Armours" 0
set_chaos_recipe_enabled_for "Helmets" 1
set_chaos_recipe_enabled_for "Gloves" 1
set_chaos_recipe_enabled_for "Boots" 1
set_chaos_recipe_enabled_for "Rings" 0
set_chaos_recipe_enabled_for "Amulets" 1
set_chaos_recipe_enabled_for "Belts" 0
get_all_chaos_recipe_statuses
'''

# Note: '...' indicates we don't check this output
kTestBatchExpectedOutputList = [
    '...',  # won't check get_all_currency_tiers initial output
    '', '', '2',  # set_currency_to_tier/get_tier_of_currency
    '', '4',  # set/get_currency_tier_min_visible_stack_size 2 (4)
    '', '1',  # set/get_currency_tier_min_visible_stack_size twisdom (1)
    '...', '', '1',  # set/get_hide_unique_items_above_tier
    '', '18',  # set/get_gem_min_quality
    '', '13',  # set/get_hide_maps_below_tier
    '...', '', '', '1 0', '0 0',  # set/get_flask_visibility
    '', '', '', '', '', '', '', '', '...']  # chaos recipe visibility checked separately

kTestBatchExpectedChaosRecipeVisbilityMap = {
    "Weapons" : 0,
    "Body Armours" : 0,
    "Helmets" : 1,
    "Gloves" : 1,
    "Boots" : 1,
    "Rings" : 0,
    "Amulets" : 1,
    "Belts" : 0}
    
def TestRunBatch():
    print('Running TestBatch...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    helper.WriteToFile(kTestBatchString, kBackendCliInputFilename)
    CallCliFunction('run_batch')
    batch_output_string = ''.join(helper.ReadFile(kBackendCliOutputFilename))
    batch_output_string = batch_output_string[:-3]  # trim off trailing '\n@\n'
    batch_output_list = batch_output_string.split('\n@\n')
    # Check outputs
    CHECK(len(batch_output_list) == len(kTestBatchExpectedOutputList))
    for output_index in range(len(kTestBatchExpectedOutputList)):
        function_output_string = batch_output_list[output_index]
        expected_function_output_string = kTestBatchExpectedOutputList[output_index]
        if (expected_function_output_string != '...'):
            CHECK(function_output_string == expected_function_output_string)
    # Check chaos recipe visibility outputs
    chaos_recipe_visibiility_list = [line.split(';') for line in batch_output_list[-1].split('\n')]
    for item_slot, visibility_string in chaos_recipe_visibiility_list:
        visibility_flag = int(visibility_string)
        CHECK(visibility_flag == kTestBatchExpectedChaosRecipeVisbilityMap[item_slot])
# End TestRunBatch

def RunAllTests():
    print('Launching test suite')
    print('Note: test suite currently covers all backend functions except:')
    print('\n'.join([' - get_all_profile_names', ' - set_active_profile',
                     ' - get_rule_matching_item (use test_rule_matching for this)']))
    print()
    TestSetRuleVisibility()
    TestCurrency()
    TestEssences()
    TestDivCards()
    TestUniqueItems()
    TestUniqueMaps()
    TestOils()
    TestHideMapsBelowTier()
    TestGemQuality()
    TestFlaskQuality()
    TestFlasks()
    TestRgbItems()
    TestChaosRecipe()
    TestRunBatch()
# End RunAllTests

def main():
    logger.InitializeLog(kTestLogFilename)
    RunAllTests()
    print('All tests completed successfully!\n')
# End main

if (__name__ == '__main__'):
    main()
