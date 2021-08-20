import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

def main():
    logger.InitializeLog('example.log')
    loot_filter = LootFilter(config.kInputLootFilterFilename, config.kOutputLootFilterFilename)
    loot_filter.SaveToFile()
    
if (__name__ == '__main__'):
    main()
