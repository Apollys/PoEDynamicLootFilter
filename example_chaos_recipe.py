import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

def ChaosRecipeExample():
    loot_filter = LootFilter(config.kInputLootFilterFilename)
    print('Hiding Body Armours and Helmets')
    loot_filter.SetChaosRecipeItemSlotEnabled("Body Armours", False)
    loot_filter.SetChaosRecipeItemSlotEnabled("Helmets", False)
    body_armours_enabled: bool = loot_filter.IsChaosRecipeItemSlotEnabled("Body Armours")
    weapons_enabled: bool = loot_filter.IsChaosRecipeItemSlotEnabled("Weapons")
    print('Body Armours enabled:', body_armours_enabled)
    print('Weapons enabled:', weapons_enabled)
    loot_filter.SaveToFile(config.kOutputLootFilterFilename)
# End ChaosRecipeExample
    
def main():
    logger.InitializeLog('example.log')
    ChaosRecipeExample()
    
if (__name__ == '__main__'):
    main()
