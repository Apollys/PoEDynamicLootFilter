import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

from backend_cli import kTestOutputLootFilterFilename, kTestProfileFullpath

def main():
    logger.InitializeLog('example.log')
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             kTestOutputLootFilterFilename,
                             kTestProfileFullpath)
    loot_filter.SaveToFile()
    print('Loot filter saved to', kTestOutputLootFilterFilename)
    
if (__name__ == '__main__'):
    main()
