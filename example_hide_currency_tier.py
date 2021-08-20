import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

def HideCurrencyTierExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Hide currency by tier:
    tier_number = 5
    print('Hiding T{} currency...\n'.format(tier_number))
    # Look up rule by type and tier
    type_name = 'currency'
    tier_name = consts.kCurrencyTierNames[tier_number]
    [rule] = loot_filter.GetRulesByTypeTier(type_name, tier_name)
    print('Found rule:\n')
    print(rule)
    # Set visibility: options are kShow, kHide, kDisable (comment out rule)
    rule.SetVisibility(RuleVisibility.kDisable)
    print('\nSetting visibility to "Disable" produces the following rule:\n')
    print(rule)
    rule.SetVisibility(RuleVisibility.kHide)
    print('\nSetting visibilty to "Hide" gives the following rule:\n')
    print(rule)
    print('\nSaving updated filter to', config.kPathOfExileLootFilterFullpath)
    loot_filter.SaveToFile()

def main():
    logger.InitializeLog('example.log')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath, config.kPathOfExileLootFilterFullpath)
    HideCurrencyTierExample(loot_filter)
    

if (__name__ == '__main__'):
    main()
