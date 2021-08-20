import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

def MoveCurrencyBetweenTiersExample(loot_filter):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    # Move Blessed Orbs "down" one tier (+1 numerically to the tier)
    currency_name = 'Blessed Orb'
    tier_delta = +1
    loot_filter.AdjustTierOfCurrency(currency_name, tier_delta)
    # Desperate for chromes! Move currency to specific tier
    currency_name = 'Chromatic Orb'
    target_tier = 2
    loot_filter.SetCurrencyToTier(currency_name, target_tier)
    # Save new filter (diff input and output filter to see changes)
    loot_filter.SaveToFile()

def main():
    logger.InitializeLog('example.log')
    loot_filter = LootFilter(config.kInputLootFilterFilename, config.kOutputLootFilterFilename)
    MoveCurrencyBetweenTiersExample(loot_filter)
    
if (__name__ == '__main__'):
    main()
