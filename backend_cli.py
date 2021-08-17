'''
This file defines the command-line interface for the AHK frontend
to call the Python backend.  The general call format is:

 > python3 backend_cli.py <function_name> <function_parameters>

Return values of functions will be placed in the file "backend_cli.output",
formatted as specified by the frontend developer.  (Note: make sure
calls to the cli are synchronous if return values are to be used,
so you ensure data is written before you try to read it.)

Currently supported functions are:
 - "adjust_currency_tier": moves a given currency type by a relative tier_delta
   Paramters: base_type, tier_delta
   Example usage: > python3 backend_cli.py "Chromatic Orb" -2
   
The input and output filter filepaths are specified in config.py.
(Eventually these will be the same, but for testing they're distinct.)
'''

import sys
from typing import List

import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

kLogFilename = 'backend_cli.log'
kReturnFilename = 'backend_cli.output'

def CheckNumParams(params_list: List[str], required_num_params: int):
    CheckType(params_list, 'params_list', list)
    CheckType(required_num_params, 'required_num_params', int)
    if (len(params_list) != required_num_params):
        error_message: str = ('incorrect number of parameters given for '
                              'function {}: required {}, got {}').format(
                                   sys.argv[1], required_num_params, len(params_list))
        logger.Log('Error: ' + error_message)
        raise RuntimeError(error_message)
# End CheckNumParams

def DelegateFunctionCall(loot_filter: LootFilter, function_name: str, function_params):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    CheckType(function_name, 'function_name', str)
    CheckType(function_params, 'function_params_list', list)
    if (function_name == 'adjust_currency_tier'):
        CheckNumParams(function_params, 2)
        currency_name: str = function_params[0]
        tier_delta: int = int(function_params[1])
        loot_filter.AdjustTierOfCurrency(currency_name, tier_delta)
        loot_filter.SaveToFile(config.kOutputLootFilterFilename)
# End DelegateFunctionCall
        
def main():
    print('sys.argv =', sys.argv)
    logger.InitializeLog(kLogFilename)
    loot_filter = LootFilter(config.kInputLootFilterFilename)
    if (len(sys.argv) < 2):
        error_message: str = 'no function specified, too few command line arguments given'
        logger.Log('Error: ' + error_message)
        raise RuntimeError(error_message)
    function_name: str = sys.argv[1]
    DelegateFunctionCall(loot_filter, function_name, sys.argv[2:])
# End main    

if (__name__ == '__main__'):
    main()
