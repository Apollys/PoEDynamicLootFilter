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
from type_checker import CheckType, CheckType2

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
    full_command: str = 'python3 backend_cli.py ' + function_call + ' ' + kTestProfileName
    return_value = os.system(full_command)
    CHECK(return_value == 0)
# End RunCommand

def TestSetRuleVisibility():
    print('Running TestSetRuleVisibility...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    type_tag = consts.kCurrencyTypeTag
    tier_tag = consts.kCurrencyTierNames[1]
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

def TestHideMapsBelowTier():
    print('Running TestHideMapsBelowTier...')
    ResetTestProfile()
    CallCliFunction('import_downloaded_filter')
    CallCliFunction('get_hide_maps_below_tier')
    CheckOutput('0')
    for i in range(3):
        tier = random.randint(0, 16)
        CallCliFunction('set_hide_maps_below_tier {}'.format(tier))
        CallCliFunction('get_hide_maps_below_tier')
        CheckOutput(str(tier))
# End TestHideMapsBelowTier

# ========================= TODO: update all tests below this line ==========================

def TestCurrency():
    print('Running TestCurrency...')
    loot_filter = LootFilter(test_consts.kDownloadedLootFilterFullpath,
                             test_consts.kPathOfExileLootFilterFullpath,
                             test_consts.kProfileFullpath)
    type_name = 'currency'
    for tier in range(1, 10):
        currency_names = loot_filter.GetAllCurrencyInTier(tier)
        # Test SetCurrencyToTier with random currency
        currency_name = random.choice(currency_names)
        target_tier = random.randint(1, 9)
        loot_filter.SetCurrencyToTier(currency_name, target_tier)
        CHECK(loot_filter.GetTierOfCurrency(currency_name) == target_tier)
        # Test AdjustTierOfCurrency with random currency
        currency_name = random.choice(currency_names)
        current_tier = loot_filter.GetTierOfCurrency(currency_name)
        target_tier = random.randint(1, 9)
        tier_delta = target_tier - current_tier
        loot_filter.AdjustTierOfCurrency(currency_name, tier_delta)
        CHECK(loot_filter.GetTierOfCurrency(currency_name) == target_tier)
    for tier in list(range(1, 10)) + ['twisdom', 'tportal']:
        desired_visibility = random.choice([RuleVisibility.kShow, RuleVisibility.kHide])
        loot_filter.SetCurrencyTierVisibility(tier, desired_visibility)
        CHECK(loot_filter.GetCurrencyTierVisibility(tier) == desired_visibility)
# End TestCurrency

def TestChaosRecipe():
    print('Running TestChaosRecipe...')
    loot_filter = LootFilter(test_consts.kDownloadedLootFilterFullpath,
                             test_consts.kPathOfExileLootFilterFullpath,
                             test_consts.kProfileFullpath)
    desired_enabled_status_map = {item_slot : random.choice([True, False])
                                  for item_slot in consts.kChaosRecipeItemSlots}
    for item_slot, desired_enabled_status in desired_enabled_status_map.items():
        loot_filter.SetChaosRecipeEnabledFor(item_slot, desired_enabled_status)
    for item_slot, desired_enabled_status in desired_enabled_status_map.items():
        enabled_status = loot_filter.IsChaosRecipeEnabledFor(item_slot)
        CHECK(enabled_status == desired_enabled_status)
# End TestChaosRecipe

def TestRunBatchCli():
    print('Running TestBatchCli...')
    shutil.copyfile(test_consts.kTestBatchFullpath, kBackendCliInputFilename)
    import_filter_command = 'python3 backend_cli.py TEST import_downloaded_filter only_if_missing'
    os.system(import_filter_command)
    run_batch_command = 'python3 backend_cli.py TEST run_batch'
    os.system(run_batch_command)
# End TestRunBatchCli

def TestBackendCli():
    print('Running TestBackendCli...')
    function_call_strings = ['import_downloaded_filter',
                             'adjust_currency_tier "Chromatic Orb" -2',
                             'set_currency_tier "Chromatic Orb" 5',
                             'get_all_currency_tiers',
                             'set_hide_currency_above_tier 8',
                             'get_hide_currency_above_tier',
                             'set_hide_map_below_tier 14',
                             'get_hide_map_below_tier',
                             'set_flask_rule_enabled_for "Quartz Flask" 1',
                             'set_flask_rule_enabled_for "Diamond Flask" 1',
                             'set_flask_rule_enabled_for "Quartz Flask" 0',
                             'set_flask_rule_enabled_for "Diamond Flask" 0',
                             'is_flask_rule_enabled_for "Quicksilver Flask"',
                             'get_all_enabled_flask_types',
                             'set_chaos_recipe_enabled_for Weapons 0',
                             'is_chaos_recipe_enabled_for "Body Armours"',
                             'get_all_chaos_recipe_statuses',
                             'undo_last_change']
    for function_call_string in function_call_strings:
        command_string = 'python3 backend_cli.py TEST ' + function_call_string
        return_value = os.system(command_string)
        CHECK(return_value == 0)
# End TestBackendCli

def RunAllTests():
    TestSetRuleVisibility()
    TestHideMapsBelowTier()
    #TestCurrency()
    #TestChaosRecipe()
    #TestRunBatchCli()
    #ResetTestProfile()
    #TestBackendCli()
# End RunAllTests

def main():
    logger.InitializeLog(kTestLogFilename)
    RunAllTests()
    print('All tests completed successfully!')
# End main

if (__name__ == '__main__'):
    main()
