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
   Example usage: > python3 backend_cli.py adjust_currency_tier "Chromatic Orb" -2
   
The input and output filter filepaths are specified in config.py.
(Eventually these will be the same, but for testing they're distinct.)

Error handling:  if anything goes wrong while the python script is executing,
all relevant error messages will be written to "backend_cli.log", since the
standard output will not be available when the scripts are run via AHK.
For example, running the following command:
 > python3 backend_cli.py adjust_currency_tier "Chromatic Orb" a
will generate the error message:
"ValueError: invalid literal for int() with base 10: 'a'",
which will be logged to the log file along with the stack trace.
'''

import sys
import traceback
from typing import List

import config
import consts
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
from type_checker import CheckType

kLogFilename = 'backend_cli.log'
kOutputFilename = 'backend_cli.output'

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

def WriteOutput(output_string: str):
    CheckType(output_string, 'output_string', str)
    with open(kOutputFilename, 'w') as output_file:
        output_file.write(output_string)
# End WriteOutput

def DelegateFunctionCall(loot_filter: LootFilter, function_name: str, function_params):
    CheckType(loot_filter, 'loot_filter', LootFilter)
    CheckType(function_name, 'function_name', str)
    CheckType(function_params, 'function_params_list', list)
    if (function_name == 'adjust_currency_tier'):
        '''
        adjust_currency_tier <currency_name> <tier_delta>
         - Moves a given currency type by a relative tier_delta
         - Output: None
         - Example: > python3 backend_cli.py adjust_currency_tier "Chromatic Orb" -2
        '''
        CheckNumParams(function_params, 2)
        currency_name: str = function_params[0]
        tier_delta: int = int(function_params[1])
        loot_filter.AdjustTierOfCurrency(currency_name, tier_delta)
        loot_filter.SaveToFile(config.kOutputLootFilterFilename)
    elif (function_name == 'get_currency_tiers'):
        '''
        get_currency_tiers
         - Output: newline-separated sequence of `"<currency_name>";<tier>`,
           one per currency type
         - Example: > python3 backend_cli.py get_currency_tiers
        '''
        CheckNumParams(function_params, 0)
        output_string = ''
        for tier in consts.kCurrencyTierNames:
            currency_names = loot_filter.GetAllCurrencyInTier(tier)
            output_string += ''.join(('"' + currency_name + '";' + str(tier) + '\n')
                                        for currency_name in currency_names)
        WriteOutput(output_string)
# End DelegateFunctionCall
        
def main():
    # Initialize
    logger.InitializeLog(kLogFilename)
    loot_filter = LootFilter(config.kInputLootFilterFilename)
    argv_info_message: str = 'Info: sys.argv = ' + str(sys.argv)
    print(argv_info_message)
    logger.Log(argv_info_message)
    # Check that there at least exists a function name in argv
    if (len(sys.argv) < 2):
        error_message: str = 'no function specified, too few command line arguments given'
        logger.Log('Error: ' + error_message)
        raise RuntimeError(error_message)
    # Delegate function call based on name
    function_name: str = sys.argv[1]
    try:
        DelegateFunctionCall(loot_filter, function_name, sys.argv[2:])
    except Exception as e:
        traceback_message = traceback.format_exc()
        logger.Log(traceback_message)
        raise e
# End main    

if (__name__ == '__main__'):
    main()
