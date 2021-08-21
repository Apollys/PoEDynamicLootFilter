import random
import shlex
import subprocess

from backend_cli import kInputFilename as kBackendCliInputFilename
import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
import test_consts
from type_checker import CheckType

def CHECK(expr: bool):
    if (not expr):
        raise RuntimeError('CHECK failed: expression evaluated to False')
# End CHECK

def ResetTestProfile():
    open(test_consts.kTestProfileFullpath, 'w').close()
    open(test_consts.kTestPoELootFilterFilename, 'w').close()
# End ResetTestProfile

def TestChangeRuleVisibility():
    print('Running TestChangeRuleVisibility...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             test_consts.kTestPoELootFilterFilename,
                             test_consts.kTestProfileFullpath)
    type_name = 'currency'
    tier_name = consts.kCurrencyTierNames[1]
    rule = loot_filter.type_tier_rule_map[type_name][tier_name]
    rule.SetVisibility(RuleVisibility.kShow)
    rule.SetVisibility(RuleVisibility.kHide)
    rule.SetVisibility(RuleVisibility.kDisable)
    CHECK(all(line.startswith('#') for line in rule.text_lines))
# End TestChangeRuleVisibility

def TestHideMapsBelowTier():
    print('Running TestHideMapsBelowTier...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             test_consts.kTestPoELootFilterFilename,
                             test_consts.kTestProfileFullpath)
    CHECK(loot_filter.GetHideMapsBelowTierTier() == config.kHideMapsBelowTier)
    for i in range(10):
        tier = random.randint(0, 16)
        loot_filter.SetHideMapsBelowTierTier(tier)
        CHECK(loot_filter.GetHideMapsBelowTierTier() == tier)
    loot_filter.SaveToFile()
# End TestHideMapsBelowTier

def TestCurrency():
    print('Running TestCurrency...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             test_consts.kTestPoELootFilterFilename,
                             test_consts.kTestProfileFullpath)
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
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             test_consts.kTestPoELootFilterFilename,
                             test_consts.kTestProfileFullpath)
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
    subprocess.run(['cp', 'backend_cli.test_input', kBackendCliInputFilename])
    run_batch_command = 'python3 backend_cli.py TEST import_downloaded_filter only_if_missing'
    subprocess.run(shlex.split(run_batch_command))
    run_batch_command = 'python3 backend_cli.py TEST run_batch'
    subprocess.run(shlex.split(run_batch_command))
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
        cli_params_list = (['python3', 'backend_cli.py', 'TEST']
                            + shlex.split(function_call_string))
        completed_process = subprocess.run(cli_params_list)
        CHECK(completed_process.returncode == 0)
# End TestBackendCli

def RunAllTests():
    ResetTestProfile()
    TestChangeRuleVisibility()
    TestHideMapsBelowTier()
    TestCurrency()
    TestChaosRecipe()
    TestRunBatchCli()
    ResetTestProfile()
    TestBackendCli()
# End RunAllTests

def main():
    logger.InitializeLog(test_consts.kTestLogFilename)
    RunAllTests()
    print('All tests completed successfully!')
# End main

if (__name__ == '__main__'):
    main()
