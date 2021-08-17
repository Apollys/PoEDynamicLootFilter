from typing import Dict, List, Tuple

import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

def RuleSearchExample(loot_filter: LootFilter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Find all sections matching keyword(s)
    keyword = 'currency'  # case insensitive
    matching_section_names: List[str] = loot_filter.SearchSectionNames(keyword)
    print('All sections matching keyword "', keyword, ':', sep='')
    print(' ->', '\n -> '.join(matching_section_names))
    print()
    
    # Find all rules of sections matching keyword search
    keyword = 'Regular Currency Tiering'
    matching_section_names: List[str] = loot_filter.SearchSectionNames(keyword)
    print('All rules matching keyword "', keyword, ':\n', sep='')
    for section_name in matching_section_names:
        section_rules: List[LootFilterRule] = loot_filter.GetSectionRules(section_name)
        print('### Section:', section_name, '###', '\n')
        for rule in section_rules:
            rule_start_line_number = rule.start_line_index + 1
            print('# Rule from line', rule_start_line_number, ' in loot filter:\n')
            print(rule)
            print('\n* * * * * * * * * * * * * * * * * * * *\n')
    
    # Find tier 1 currency rule
    section_name = 'Currency - Regular Currency Tiering'
    t1_currency_identifier = '$type->currency $tier->t1'
    section_rules: List[LootFilterRule] = loot_filter.GetSectionRules(section_name)
    print(type(section_rules))
    print(type(section_rules[0]))
    print('Searching for tier 1 currency rule...\n')
    for rule in section_rules:
        if (t1_currency_identifier in str(rule)):
            rule_start_line_number = rule.start_line_index + 1
            print('Found rule from line', rule_start_line_number, ' in loot filter:\n')
            print('type = "', rule.type, '", tier = "', rule.tier, '"\n', sep='')
            print(rule)
            print('\n* * * * * * * * * * * * * * * * * * * *\n')
            # Modify rule visibility and save filter to file
            rule.SetVisibility(RuleVisibility.kShow)
            rule.SetVisibility(RuleVisibility.kHide)
            rule.SetVisibility(RuleVisibility.kDisable)
    loot_filter.SaveToFile(kOutputLootFilterFilename)
    # Now just reload filter in-game and changes are applied
    
    # End RuleSearchExample()

def HideCurrencyTierExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Hide currency by tier:
    tier_number = 5
    print('Hiding T{} currency...\n'.format(tier_number))
    type_name = 'currency'
    tier_name = kCurrencyTierNames['t' + str(tier_number)]
    [found_currency_rule] = loot_filter.GetRulesByTypeTier(type_name, tier_name)
    print('Found rule:\n')
    print(found_currency_rule)
    found_currency_rule.SetVisibility(RuleVisibility.kHide)
    print('\nReplaced with rule:\n')
    print(found_currency_rule)
    print('\nSaving new filter to', kOutputLootFilterFilename)
    loot_filter.SaveToFile(kOutputLootFilterFilename)
    
def MoveCurrencyBetweenTiersExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Move Blessed Orbs down a tier
    base_type_name = 'Blessed Orb'
    starting_tier_number = 5
    target_tier_number = starting_tier_number + 1
    # Look up currency by tier
    type_name = 'currency'
    starting_tier_name = kCurrencyTierNames['t' + str(starting_tier_number)]
    [starting_currency_rule] = loot_filter.GetRulesByTypeTier(type_name, starting_tier_name)
    starting_currency_rule.RemoveBaseType(base_type_name)
    target_tier_name = kCurrencyTierNames['t' + str(target_tier_number)]
    [target_currency_rule] = loot_filter.GetRulesByTypeTier(type_name, target_tier_name)
    target_currency_rule.AddBaseType(base_type_name)
    print('Moved BaseType: {} from tier {} to tier {}\n'.format(
            base_type_name, starting_tier_number, target_tier_number))
    print(starting_currency_rule)
    print('\n* * * * * * * * * * * * * * * * * * * *\n')
    print(target_currency_rule)
    loot_filter.SaveToFile(kOutputLootFilterFilename)

def MakeChaosRecipeRulesExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    chaos_recipe_rules = [LootFilterRule(rule_string, -1) 
                          for rule_string in consts.kChaosRecipeRuleStrings]
    print('Generated chaos recipe rules:\n')
    for rule in chaos_recipe_rules:
        print(rule)
        print('\n* * * * * * * * * * * * * * * * * * * * * * * * * *\n')

def main():
    logger.InitializeLog('example.log')
    loot_filter = LootFilter(config.kInputLootFilterFilename)
    MakeChaosRecipeRulesExample(loot_filter)
    

if (__name__ == '__main__'):
    main()
