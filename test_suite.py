import os
import random

import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

kTestLogFilename = 'test_suite.log'
kTestOutputLootFilterFilename = 'test_suite_output.filter'

def CHECK(expr: bool):
    if (not expr):
        raise RuntimeError('CHECK failed: expression evaluated to False')
# End CHECK

def TestChangeRuleVisibility():
    print('Running TestChangeRuleVisibility...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath)
    type_name = 'currency'
    tier_name = consts.kCurrencyTierNames[1]
    [rule] = loot_filter.type_tier_rule_map[type_name][tier_name]
    rule.SetVisibility(RuleVisibility.kShow)
    rule.SetVisibility(RuleVisibility.kHide)
    rule.SetVisibility(RuleVisibility.kDisable)
    CHECK(all(line.startswith('#') for line in rule.text_lines))
# End TestChangeRuleVisibility

def TestHideMapsBelowTier():
    print('Running TestHideMapsBelowTier...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath)
    CHECK(loot_filter.GetHideMapsBelowTierTier() == config.kHideMapsBelowTier)
    for i in range(10):
        tier = random.randint(0, 16)
        loot_filter.SetHideMapsBelowTierTier(tier)
        CHECK(loot_filter.GetHideMapsBelowTierTier() == tier)
    loot_filter.SaveToFile(kTestOutputLootFilterFilename)
# End TestHideMapsBelowTier

def TestCurrency():
    print('Running TestCurrency...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath)
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
# End TestCurrency

def TestChaosRecipe():
    print('Running TestChaosRecipe...')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath)
    desired_enabled_status_map = {item_slot : random.choice([True, False])
                                  for item_slot in consts.kChaosRecipeItemSlots}
    for item_slot, desired_enabled_status in desired_enabled_status_map.items():
        loot_filter.SetChaosRecipeEnabledFor(item_slot, desired_enabled_status)
    for item_slot, desired_enabled_status in desired_enabled_status_map.items():
        enabled_status = loot_filter.IsChaosRecipeEnabledFor(item_slot)
        CHECK(enabled_status == desired_enabled_status)
# End TestChaosRecipe

def TestBackendCli():
    print('Running TestBackendCli...')
    test_function_calls = ['import_downloaded_filter',
                           'adjust_currency_tier "Chromatic Orb" -2',
                           'set_currency_tier "Chromatic Orb" 5',
                           'get_all_currency_tiers',
                           'set_hide_map_below_tier 14',
                           'get_hide_map_below_tier',
                           'set_chaos_recipe_enabled_for Weapons 0',
                           'is_chaos_recipe_enabled_for "Body Armours"']
    for function_call in test_function_calls:
        return_value = os.system('python3 backend_cli.py ' + function_call)
        CHECK(return_value == 0)
# End TestBackendCli

def RunAllTests():
    TestChangeRuleVisibility()
    TestHideMapsBelowTier()
    TestCurrency()
    TestChaosRecipe()
    TestBackendCli()
# End RunAllTests

def main():
    logger.InitializeLog(kTestLogFilename)
    RunAllTests()
    print('All tests completed successfully!')
# End main

if (__name__ == '__main__'):
    main()
