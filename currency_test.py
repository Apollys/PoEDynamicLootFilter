from backend_cli import kInputFilename as kBackendCliInputFilename
from backend_cli import kTestOutputLootFilterFilename, kTestProfileFullpath
import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

kTestLogFilename = 'test_suite.log'

def CHECK(expr: bool):
    if (not expr):
        raise RuntimeError('CHECK failed: expression evaluated to False')
# End CHECK

def main():
    logger.InitializeLog(kTestLogFilename)
    loot_filter = LootFilter(config.kDownloadedLootFilterFullpath,
                             kTestOutputLootFilterFilename, kTestProfileFullpath)
    type_name = 'currency'
    currency_name = 'Chromatic Orb'
    target_tier = 1
    loot_filter.SetCurrencyToTier(currency_name, target_tier)
    loot_filter.SaveToFile()
    print(loot_filter.GetTierOfCurrency(currency_name))
    #CHECK(loot_filter.GetTierOfCurrency(currency_name) == target_tier)
    
main()
