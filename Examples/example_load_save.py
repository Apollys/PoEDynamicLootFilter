import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
import test_consts
from type_checker import CheckType

def main():
    logger.InitializeLog(test_consts.kTestLogFilename)
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             test_consts.kTestPoELootFilterFilename,
                             test_consts.kTestProfileFullpath)
    loot_filter.SaveToFile()
    print('Loot filter saved to', test_consts.kTestPoELootFilterFilename)
    
if (__name__ == '__main__'):
    main()
