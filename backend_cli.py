'''
This file defines the command-line interface for the AHK frontend
to call the Python backend.  The general call format is:

 > python3 backend_cli.py <function_name> <function_parameters>

Return values of functions will be placed in the file "backend_cli.output",
formatted as specified by the frontend developer.  (Note: make sure
calls to the cli are synchronous if return values are to be used,
so you ensure data is written before you try to read it.)

Scroll down to DelegateFunctionCall() to see documentation of all supported functions.
   
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

def DelegateFunctionCall(function_name: str, function_params):
    CheckType(function_name, 'function_name', str)
    CheckType(function_params, 'function_params_list', list)
    input_loot_filter_fullpath = (config.kDownloadedLootFilterFullpath
                                  if function_name == 'import_downloaded_filter'
                                  else config.kPathOfExileLootFilterFullpath)
    loot_filter = LootFilter(input_loot_filter_fullpath)
    if (function_name == 'import_downloaded_filter'):
        '''
        import_downloaded_filter
         - Reads the filter located in the downloads directory, applies all DLF
           custom changes to it, and saves the result in the Path Of Exile directory.
           See config.py to configure filter file paths and names.
         - Output: None
         - Example: > python3 backend_cli.py import_downloaded_filter
        '''
        CheckNumParams(function_params, 0)
        # TODO: once profile saving is implemented, apply all saved changes to filter here
        loot_filter.SaveToFile(config.kPathOfExileLootFilterFullpath)
    elif (function_name == 'adjust_currency_tier'):
        '''
        adjust_currency_tier <currency_name: str> <tier_delta: int>
         - Moves the given currency type by a relative tier_delta
         - Output: None
         - Example: > python3 backend_cli.py adjust_currency_tier "Chromatic Orb" -2
        '''
        CheckNumParams(function_params, 2)
        currency_name: str = function_params[0]
        tier_delta: int = int(function_params[1])
        loot_filter.AdjustTierOfCurrency(currency_name, tier_delta)
        loot_filter.SaveToFile(config.kPathOfExileLootFilterFullpath)
    elif (function_name == 'set_currency_tier'):
        '''
        set_currency_tier <currency_name: str> <tier: int>
         - Moves the given currency type to the specified tier
         - Output: None
         - Example: > python3 backend_cli.py set_currency_tier "Chromatic Orb" 5
        '''
        CheckNumParams(function_params, 2)
        currency_name: str = function_params[0]
        target_tier: int = int(function_params[1])
        loot_filter.SetCurrencyToTier(currency_name, target_tier)
        loot_filter.SaveToFile(config.kPathOfExileLootFilterFullpath)
    elif (function_name == 'get_currency_tiers'):
        '''
        get_currency_tiers
         - Output: newline-separated sequence of `<currency_name: str>;<tier: int>`,
           one per currency type
         - Example: > python3 backend_cli.py get_currency_tiers
        '''
        CheckNumParams(function_params, 0)
        output_string = ''
        for tier in consts.kCurrencyTierNames:
            currency_names = loot_filter.GetAllCurrencyInTier(tier)
            output_string += ''.join((currency_name + ';' + str(tier) + '\n')
                                        for currency_name in currency_names)
        WriteOutput(output_string)
    elif (function_name == 'set_hide_map_below_tier'):
        '''
        set_hide_map_below_tier <tier: int>
         - Sets the map tier below which all will be hidden (use 0/1 to show all)
         - Output: None
         - Example: > python3 backend_cli.py set_hide_map_below_tier 14
        '''
        tier: int = int(function_params[0])
        loot_filter.SetHideMapsBelowTierTier(tier)
        loot_filter.SaveToFile(config.kPathOfExileLootFilterFullpath)
    elif (function_name == 'get_hide_map_below_tier'):
        '''
        get_hide_map_below_tier
         - Output: a single number, the tier below which all maps are hidden
         - Example: > python3 backend_cli.py get_hide_map_below_tier
        '''
        output_string = str(loot_filter.GetHideMapsBelowTierTier())
        WriteOutput(output_string)
    elif (function_name == 'set_chaos_recipe_enabled_for'):
        '''
        set_chaos_recipe_enabled_for <item_slot: str> <enable_flag: int>
         - <item_slot> is one of: "Weapons", "Body Armours", "Helmets", "Gloves",
           "Boots", "Amulets", "Rings", "Belts"
         - enable_flag is 1 for True (enable), 0 for False (disable)
         - Output: None
         - Example: > python3 backend_cli.py set_chaos_recipe_enabled_for Weapons 0
        '''
        item_slot: str = function_params[0]
        enable_flag: bool = bool(int(function_params[1]))
        loot_filter.SetChaosRecipeEnabledFor(item_slot, enable_flag)
        loot_filter.SaveToFile(config.kPathOfExileLootFilterFullpath)
    elif (function_name == 'is_chaos_recipe_enabled_for'):
        '''
        is_chaos_recipe_enabled_for <item_slot: str>
         - <item_slot> is one of: "Weapons", "Body Armours", "Helmets", "Gloves",
           "Boots", "Amulets", "Rings", "Belts"
         - Output: "1" if chaos recipe items are showing for the given item_slot, else "0"
         - Example: > python3 backend_cli.py is_chaos_recipe_enabled_for "Body Armours"
        '''
        item_slot: str = function_params[0]
        output_string = str(int(loot_filter.IsChaosRecipeEnabledFor(item_slot)))
        WriteOutput(output_string)
    else:
        error_message: str = 'Function "{}" not found'.format(function_name)
        logger.Log('Error: ' + error_message)
        raise RuntimeError(error_message)
        
# End DelegateFunctionCall
        
def main():
    # Initialize
    logger.InitializeLog(kLogFilename)
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
        DelegateFunctionCall(function_name, sys.argv[2:])
    except Exception as e:
        traceback_message = traceback.format_exc()
        logger.Log(traceback_message)
        raise e
# End main    

if (__name__ == '__main__'):
    main()
