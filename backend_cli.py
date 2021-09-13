'''
This file defines the command-line interface for the AHK frontend
to call the Python backend.  The general call format is:

 > python3 backend_cli.py <function_name> <function_parameters...> <profile_name (if required>

Return values of functions will be placed in the file "backend_cli.output",
formatted as specified by the frontend developer.  (Note: make sure
calls to the cli are synchronous if return values are to be used,
so you ensure data is written before you try to read it.)

Some functions do not require a profile_name parameter, specifically those which
do not interact with the filter in any way (for now, this is simply the setters and getters
for profile names).

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

Testing feature:
 - Insert "TEST" as the first argument after "python3 backend_cli.py" to run tests
 - This wil write output to test output filter, rather than the PathOfExile filter path
 - This will also save all profile updates in a separate testing profile so as to not ruin
   one's real profile(s).  Used in all test_suite.py calls.
'''

import os
from pathlib import Path
import shlex
import shutil
import sys
import traceback
from typing import List

import consts
import file_manip
import helper
import logger
from loot_filter import RuleVisibility, LootFilterRule, LootFilter
import profile
from type_checker import CheckType

kLogFilename = 'backend_cli.log'
kInputFilename = 'backend_cli.input'
kOutputFilename = 'backend_cli.output'

# List of functions that modify the filter in any way
# This list excludes getter-only functions, which can be excluded from the profile data
# Also exclues run_batch (depends on batch functions) and import_downloaded_filter
# Excluded undo_last_change since it's rather unique and handles its own saving
kFilterMutatorFunctionNames = ['set_rule_visibility',
        'set_currency_tier', 'adjust_currency_tier',
        'set_currency_tier_visibility', 'set_hide_currency_above_tier', 
        'set_hide_uniques_above_tier', 'set_gem_min_quality', 'set_hide_maps_below_tier',
         'set_flask_visibility', 'set_chaos_recipe_enabled_for',]

# Functions that don't require a profile parameter in the CLI
# These are the functions that do not interact with the loot filter in any way
kNoProfileParameterFunctionNames = ['get_all_profile_names', 'set_active_profile']

def Error(e):
    logger.Log('Error ' + str(e))
    raise RuntimeError(e)
# End Error

def FileExists(path: str) -> bool:
    return Path(path).is_file()
# End FileExists

def CheckNumParams(params_list: List[str], required_num_params: int):
    CheckType(params_list, 'params_list', list)
    CheckType(required_num_params, 'required_num_params', int)
    if (len(params_list) != required_num_params):
        error_message: str = ('incorrect number of parameters given for '
                              'function {}: required {}, got {}').format(
                                   sys.argv[1], required_num_params, len(params_list))
        Error(error_message)
# End CheckNumParams

def WriteOutput(output_string: str):
    CheckType(output_string, 'output_string', str)
    with open(kOutputFilename, 'w') as output_file:
        output_file.write(output_string)
# End WriteOutput

# function_output_string should be the whole string containing the given function call's output
def AppendFunctionOutput(function_output_string: str):
    CheckType(function_output_string, 'function_output_string', str)
    if ((len(function_output_string) == 0) or (function_output_string[-1] != '\n')):
        function_output_string += '\n'
    with open(kOutputFilename, 'a') as output_file:
        output_file.write(function_output_string + '@\n')
# End AppendFunctionOutput

def DelegateFunctionCall(loot_filter: LootFilter or None,
                         function_name: str,
                         function_params: List[str],
                         *,  # require subsequent arguments to be named in function call
                         in_batch: bool = False,
                         suppress_output: bool = False):
    CheckType(loot_filter, 'loot_filter', (LootFilter, type(None)))
    CheckType(function_name, 'function_name', str)
    CheckType(function_params, 'function_params_list', list)
    CheckType(in_batch, 'in_batch', bool)
    CheckType(suppress_output, 'suppress_output', bool)
    # Alias config_data for convenience
    config_data = loot_filter.profile_config_data if loot_filter else None
    # 
    output_string = ''
    # Save function call to profile data if it is a mutator function
    # (kFilterMutatorFunctionNames excludes import_downloaded_filter and run_batch)
    # Note: suppress_output also functioning as an indicator to not save profile data here
    if ((function_name in kFilterMutatorFunctionNames) and not suppress_output):
        with open(config_data['ChangesFullpath'], 'a') as changes_file:
            changes_file.write(shlex.join([function_name] + function_params) + '\n')
    # =============================== Import Downloaded Filter ===============================
    if (function_name == 'import_downloaded_filter'):
        '''
        import_downloaded_filter <optional keyword: "only_if_missing">
         - Reads the filter located in the downloads directory, applies all DLF
           custom changes to it, and saves the result in the Path Of Exile directory.
         - If the argument "only_if_missing" is present, does nothing if the filter already is
           present in the Path of Exile filters directory.
         - Assumes this is NOT called as part of a batch
         - Output: None
         - Example: > python3 backend_cli.py import_downloaded_filter
         - Example: > python3 backend_cli.py import_downloaded_filter only_if_missing
        '''
        import_flag = True
        if ((len(function_params) == 1) and (function_params[0] == 'only_if_missing')):
            import_flag = not FileExists(config_data['OutputLootFilterFullpath'])
        else:
            CheckNumParams(function_params, 0)
        if (import_flag):
            changes_lines: List[str] = helper.ReadFile(config_data['ChangesFullpath'])
            for function_call_string in changes_lines:
                _function_name, *_function_params = shlex.split(function_call_string)
                DelegateFunctionCall(loot_filter, _function_name, _function_params,
                                     in_batch = True, suppress_output = True)
            loot_filter.SaveToFile()
    # ======================================= Run Batch =======================================
    # Note: cannot run_batch from within a run_batch command, as there would be no place for
    # batch function call list, and this should be unnecessary
    elif ((function_name == 'run_batch') and not in_batch):
        '''
        run_batch
         - Runs the batch of functions specified in file backend_cli.input
         - Format is one function call per line, given as: <function_name> <function_params...>
         - Output: concatenation of the outputs of all the functions, with each function output
           separated by the line containing the single character: `@`
         - Example: > python3 run_batch
        '''
        CheckNumParams(function_params, 0)
        WriteOutput('')  # clear the output file, since we will be appending output in batch
        contains_mutator = False
        function_call_list: List[str] = helper.ReadFile(kInputFilename)
        for function_call_string in function_call_list:
            # need different variable names here to not overwrite the existing ones
            _function_name, *_function_params = shlex.split(function_call_string)
            if (_function_name in kFilterMutatorFunctionNames):
                contains_mutator = True
            DelegateFunctionCall(loot_filter, _function_name, _function_params,
                                 in_batch = True, suppress_output = False)
        # Check if batch contained a mutator and save filter if so
        if (contains_mutator):
            loot_filter.SaveToFile()
    # ========================================== Profile ==========================================
    elif (function_name == 'get_all_profile_names'):
        '''
        get_all_profile_names
         - Note: Does *not* take a <profile_name> parameter
         - Output: newline-separated list of all profile names, with currently active profile first
         - Example: > python3 get_all_profile_names
        '''
        CheckNumParams(function_params, 0)
        profile_names_list = profile.GetAllProfileNames()
        output_string += '\n'.join(profile_names_list)
    elif (function_name == 'set_active_profile'):
        '''
        set_active_profile <new_active_profile_name>
         - Note: Does *not* take a (current) <profile_name> parameter
         - Output: None
         - Example: > python3 set_active_profile TestProfile
        '''
        CheckNumParams(function_params, 1)
        profile.SetActiveProfile(function_params[0])
    elif (function_name == 'undo_last_change'):
        '''
        undo_last_change
         - Removes the last line of the current profile, then performs import_downloaded_filter
         - Assumed to never be called as part of a batch
         - Not included in mutator functions list since it's handled differently
         - Output: None
         - Example: > python3 backend_cli.py undo_last_change
        '''
        CheckNumParams(function_params, 0)
        changes_lines: List[str] = helper.ReadFile(config_data['ChangesFullpath'])
        with open(config_data['ChangesFullpath'], 'w') as changes_file:
            changes_file.writelines(changes_lines[:-1])
        DelegateFunctionCall(loot_filter, 'import_downloaded_filter', [])
    # ====================================== Rule Matching ======================================
    elif (function_name == 'get_rule_matching_item'):
        '''
        get_rule_matching_item
         - Takes an item text as input in backend_cli.input
         - Finds the rule in the PoE filter matching the item and writes it to backend_cli.output
         - The first two lines of output will be `type_tag:<type_tag>` and `tier_tag:<tier_tag>`,
           these two tags together form a unique key for the rule
         - Ignores rules with AreaLevel conditions, as well as many other niche keywords
         - Socket rules only implemented as numeric counting for now, ignores color requirements
         - Example: > python3 backend_cli.py get_rule_matching_item
        '''
        CheckNumParams(function_params, 0)
        item_text_lines: List[str] = helper.ReadFile(kInputFilename)
        type_tag, tier_tag = loot_filter.GetRuleMatchingItem(item_text_lines)
        output_string = 'type_tag:{}\ntier_tag:{}\n'.format(str(type_tag), str(tier_tag))
        if ((type_tag != None) and (tier_tag != None)):
            matched_rule = loot_filter.GetRuleByTypeTier(type_tag, tier_tag)
            output_string += '\n'.join(matched_rule.text_lines)        
    elif (function_name == 'set_rule_visibility'):
        '''
        set_rule_visibility <type_tag: str> <tier_tag: str> <visibility: {show, hide, disable}>
         - Shows, hides, or disables the rule specified by the given type and tier tags
         - The visibility parameter is one of: `show`, `hide`, `disable`
         - Output: None (for now, can output a success flag if needed)
         - Example > python3 backend_cli.py set_rule_visibility "rare->redeemer" t12 show
         - Note: quotes (either type) are necessary for tags containing a ">" character,
           since the shell will normally iterpret as the output redirection signal
        '''
        CheckNumParams(function_params, 3)
        type_tag, tier_tag, visibility_string = function_params
        kVisibilityMap = {'show': RuleVisibility.kShow, 'hide': RuleVisibility.kHide,
                          'disable': RuleVisibility.kDisable}
        success_flag = loot_filter.SetRuleVisibility(
                type_tag, tier_tag, kVisibilityMap[visibility_string])
        # Error out on incorrect tags for now to make testing easierlensing
        if (not success_flag):
            Error('Rule with type_tag="{}", tier_tag="{}" does not exist in filter'.format(
                    type_tag, tier_tag))
    # ======================================== Currency ========================================
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
    elif (function_name == 'get_all_currency_tiers'):
        '''
        get_all_currency_tiers
         - Output: newline-separated sequence of `<currency_name: str>;<tier: int>`,
           one per currency type
         - Example: > python3 backend_cli.py get_all_currency_tiers
        '''
        CheckNumParams(function_params, 0)
        output_string = ''
        for tier in consts.kCurrencyTierNames:
            currency_names = loot_filter.GetAllCurrencyInTier(tier)
            output_string += ''.join((currency_name + ';' + str(tier) + '\n')
                                        for currency_name in currency_names)
    elif (function_name == 'set_currency_tier_visibility'):
        '''
        set_currency_tier_visibility <tier: int or tier_tag: str> <visible_flag: int>
         - Sets the visibility for the given currency tier
         - First parameter may be a tier integer [1-9] or a tier tag string, such as:
           "tportal" for Portal Scrolls, "twisdom" for Wisdom Scrolls
         - visible_flag is 1 for True (enable), 0 for False (disable)
         - Output: None
         - Example: > python3 backend_cli.py set_currency_tier_visibility tportal 1
        '''
        CheckNumParams(function_params, 2)
        tier = function_params[0]
        if (tier.isdigit()): tier = int(tier)
        visible_flag = bool(int(function_params[1]))
        visibility = RuleVisibility.kShow if visible_flag else RuleVisibility.kHide
        loot_filter.SetCurrencyTierVisibility(tier, visibility)
    elif (function_name == 'get_currency_tier_visibility'):
        '''
        get_currency_tier_visibility <tier: int or tier_tag: str>
         - Parameter may be a tier integer [1-9] or a tier tag string, such as:
           "tportal" for Portal Scrolls, "twisdom" for Wisdom Scrolls
         - Output: "1" if the given currency tier is shown, "0" otherwise
         - Example: > python3 backend_cli.py get_currency_tier_visibility twisdom
        '''
        CheckNumParams(function_params, 1)
        tier = function_params[0]
        if (tier.isdigit()): tier = int(tier)
        output_string = str(int(
                loot_filter.GetCurrencyTierVisibility(tier) == RuleVisibility.kShow))
    elif (function_name == 'set_hide_currency_above_tier'):
        '''
        set_hide_currency_above_tier <tier: int>
         - Sets the currency tier "above" which all will be hidden
           (higher currency tiers are worse)
         - Output: None
         - Example: > python3 backend_cli.py set_hide_currency_above_tier 8
        '''
        CheckNumParams(function_params, 1)
        max_visible_tier: int = int(function_params[0])
        loot_filter.SetHideCurrencyAboveTierTier(max_visible_tier)
    elif (function_name == 'get_hide_currency_above_tier'):
        '''
        get_hide_currency_above_tier
         - Output: single integer, the tier above which all currency is hidden
         - Example: > python3 backend_cli.py get_hide_currency_above_tier
        '''
        CheckNumParams(function_params, 0)
        output_string = str(loot_filter.GetHideCurrencyAboveTierTier())
    # ======================================== Uniques ========================================
    elif (function_name == 'get_all_unique_tier_visibilities'):
        '''
        get_all_unique_tier_visibilities
         - Output: newline-separated sequence of `<tier>;<visible_flag>`, one per tier
         - <tier> is an integer representing the tier, <visibile_flag> is 1/0 for True/False
         - Example: > python3 backend_cli.py get_all_unique_tier_visibilities
        '''
        CheckNumParams(function_params, 0)
        for tier in range(1, consts.kMaxUniqueTier):
            output_string += str(tier) + ';' + str(int(
                    loot_filter.GetUniqueTierVisibility(tier) == RuleVisibility.kShow)) + '\n'
    elif (function_name == 'set_hide_uniques_above_tier'):
        '''
        set_hide_uniques_above_tier <tier: int>
         - Sets the unique tier "above" which all will be hidden
           (higher unique tiers are worse)
         - Output: None
         - Example: > python3 backend_cli.py set_hide_uniques_above_tier 3
        '''
        CheckNumParams(function_params, 1)
        max_visible_tier: int = int(function_params[0])
        loot_filter.SetHideUniquesAboveTierTier(max_visible_tier)
    elif (function_name == 'get_hide_uniques_above_tier'):
        '''
        get_hide_uniques_above_tier
         - Output: single integer, the tier above which all uniques are hidden
         - Example: > python3 backend_cli.py get_hide_uniques_above_tier
        '''
        CheckNumParams(function_params, 0)
        output_string = str(loot_filter.GetHideUniquesAboveTierTier())
    # ======================================= Gem Quality =======================================
    elif (function_name == 'set_gem_min_quality'):
        '''
        set_gem_min_quality <tier: int in [1, 20]>
         - Sets the minimum quality below which gems will not be shown by gem quality rules
         - Output: None
         - Example: > python3 backend_cli.py set_gem_min_quality 10
        '''
        CheckNumParams(function_params, 1)
        min_quality: int = int(function_params[0])
        loot_filter.SetGemMinQuality(min_quality)
    elif (function_name == 'get_gem_min_quality'):
        '''
        get_gem_min_quality
         - Output: single integer, minimum shown gem quality for gem quality rules
         - Example: > python3 backend_cli.py get_gem_min_quality
        '''
        CheckNumParams(function_params, 0)
        output_string = str(loot_filter.GetGemMinQuality())
    # ========================================== Maps ==========================================
    elif (function_name == 'set_hide_maps_below_tier'):
        '''
        set_hide_maps_below_tier <tier: int>
         - Sets the map tier below which all will be hidden (use 0/1 to show all)
         - Output: None
         - Example: > python3 backend_cli.py set_hide_map_below_tier 14
        '''
        min_visibile_tier: int = int(function_params[0])
        loot_filter.SetHideMapsBelowTierTier(min_visibile_tier)
    elif (function_name == 'get_hide_maps_below_tier'):
        '''
        get_hide_maps_below_tier
         - Output:  single integer, the tier below which all maps are hidden
         - Example: > python3 backend_cli.py get_hide_map_below_tier
        '''
        output_string = str(loot_filter.GetHideMapsBelowTierTier())
    # ========================================= Flasks =========================================
    elif (function_name == 'set_flask_visibility'):
        '''
        set_flask_visibility <base_type: str> <visibility_flag: int>
         - Note: this does not overwrite any original filter rules, only adds a rule on top.
           This function never hides flasks, it only modifies its own "Show" rule.
         - <base_type> is any valid flask BaseType
         - enable_flag is 1 for True (visible), 0 for False (not included in DLF rule)
         - Output: None
         - Example: > python3 backend_cli.py set_flask_rule_enabled_for "Quartz Flask" 1
        '''
        flask_base_type: str = function_params[0]
        enable_flag: bool = bool(int(function_params[1]))
        loot_filter.SetFlaskRuleEnabledFor(flask_base_type, enable_flag)
    elif (function_name == 'get_flask_visibility'):
        '''
        get_flask_visibility <base_type: str>
         - <base_type> is any valid flask BaseType
         - Output: "1" if given flask base type is shown by DLF rule, else "0"
         - Example: > python3 backend_cli.py is_flask_rule_enabled_for "Quicksilver Flask"
        '''
        flask_base_type: str = function_params[0]
        output_string = str(int(loot_filter.IsFlaskRuleEnabledFor(flask_base_type)))
    elif (function_name == 'get_all_flask_visibilities'):
        '''
        get_all_flask_visibilities
         - Output: newline-separated sequence of <flask_basetype>;<visibility_flag: int>
         - visibility_flag is 1 for True (visible), 0 for False (not included in DLF rule)
         - Example: > python3 backend_cli.py get_all_enabled_flask_types
        '''
        visible_flask_types = loot_filter.GetAllVisibleFlaskTypes()
        visible_flask_types_set = set(visible_flask_types)
        for visible_flask_base_type in visible_flask_types:
            output_string += visible_flask_base_type + ';1' + '\n'
        for flask_base_type in consts.kAllFlaskTypes:
            if flask_base_type not in visible_flask_types_set:
                output_string += flask_base_type + ';0' + '\n'
    # =================================== Chaos Recipe Rares ===================================
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
    elif (function_name == 'get_all_chaos_recipe_statuses'):
        '''
        get_all_chaos_recipe_statuses
         - Output: one line formatted as `<item_slot>;<enabled_flag>` for each item slot
         - <item_slot> is one of: "Weapons", "Body Armours", "Helmets", "Gloves",
           "Boots", "Amulets", "Rings", "Belts"
         - <enabled_flag> is "1" if chaos recipe items are showing for given item_slot, else "0"
         - Example: > python3 backend_cli.py get_all_chaos_recipe_statuses
        '''
        for item_slot in consts.kChaosRecipeItemSlots:
            enabled_flag_string = str(int(loot_filter.IsChaosRecipeEnabledFor(item_slot)))
            output_string += item_slot + ';' + enabled_flag_string + '\n'
    # ================================= Unmatched Function Name =================================
    else:
        error_message: str = 'Function "{}" not found'.format(function_name)
        logger.Log('Error: ' + error_message)
        raise RuntimeError(error_message)
    # ============================= End Function Call Delegation ================================
    # Return value is now in output_string
    if (in_batch):
        if (not suppress_output): AppendFunctionOutput(output_string)
    else:
        # If function was not run_batch, write output
        if (function_name != 'run_batch'):
            WriteOutput(output_string)
        # Save loot filter if we called a mutator function
        if (function_name in kFilterMutatorFunctionNames):
            loot_filter.SaveToFile()
# End DelegateFunctionCall

kUsageErrorString = ('ill-formed command-line call\n' +
  '  Check that the function name is spelled correctly and that the syntax is as follows:\n' +
  '  > python3 backend_cli.py <function_name> <profile_name (if required)> <function_arguments...>')

def main():
    # Initialize log
    logger.InitializeLog(kLogFilename)
    argv_info_message: str = 'Info: sys.argv = ' + str(sys.argv)
    logger.Log(argv_info_message)
    # Check that there are enough params:
    #  - For non-profile-parameterized functions: script name, function name, ...
    #  - Otherwise: script name, function name, profile name, ...
    if (len(sys.argv) < 2):
        Error(kUsageErrorString)
    _, function_name, *remaining_args = sys.argv
    profile_name = None
    required_profile_param: bool = (function_name not in kNoProfileParameterFunctionNames)
    if (required_profile_param):
        if (len(sys.argv) < 3):
            Error(kUsageErrorString)
        *function_params, profile_name = remaining_args
    else:
        function_params = remaining_args
    # If importing downloaded filter, first verify that downloaded filter exists,
    # then copy or move based on 'RemoveDownloadedFilter' value given in config
    config_data = profile.ParseProfileConfig(profile_name) if profile_name else None
    if (function_name == 'import_downloaded_filter'):
        if (not os.path.isfile(config_data['DownloadedLootFilterFullpath'])):
            Error('downloaded loot filter: "{}" does not exist'.format(
                    config_data['DownloadedLootFilterFullpath']))
        if (config_data['RemoveDownloadedFilter']):
            file_manip.MoveFile(config_data['DownloadedLootFilterFullpath'],
                                config_data['InputLootFilterFullpath'])
        else:
            file_manip.CopyFile(config_data['DownloadedLootFilterFullpath'],
                                config_data['InputLootFilterFullpath'])
    # Input filter is read from the output filter path, unless importing downloaded filter
    output_as_input_filter: bool = (function_name != 'import_downloaded_filter')
    # Delegate function call
    # Note: we create the loot filter first and pass in as a parameter,
    # so that in case of a batch, DelegateFunctionCall can call itself recursively
    loot_filter = LootFilter(profile_name, output_as_input_filter) if profile_name else None
    try:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
        DelegateFunctionCall(loot_filter, function_name, function_params)
    except Exception as e:
        traceback_message = traceback.format_exc()
        logger.Log(traceback_message)
        raise e
# End main    

if (__name__ == '__main__'):
    main()
