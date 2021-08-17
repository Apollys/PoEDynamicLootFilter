import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

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
