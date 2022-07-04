from collections import OrderedDict
import shlex
from typing import List

from backend_cli_function_info import kFunctionInfoMap
import file_helper
import profile
from type_checker import CheckType

# ============================= Helper Functions =============================

# Encloses the string in double quotes if it contains a space or single quote, otherwise just
# returns the given string.  Note: does not check for double quotes in string.
def QuoteStringIfRequired(input_string: str) -> str:
    CheckType(input_string, 'input_string', str)
    if ((" " in input_string) or ("'" in input_string)):
        return '"' + input_string + '"'
    return input_string
# End QuoteStringIfRequired

# Rather than use shlex.join, we want to join using double quotes ("Hello world") in the profile
# changes file. This improves readability, because Path of Exile items never have double quotes,
# but may have single quotes ("Sorcerer's Gloves" vs 'Sorcerer\'s Gloves').
def JoinParamsDoubleQuotes(params_list: List[str]) -> str:
    CheckType(params_list, 'params_list', list, str)
    return ' '.join(QuoteStringIfRequired(param) for param in params_list)
# End JoinParamsDoubleQuotes

# ============================== Profile Changes ==============================

# Updates the given changes_dict, adding the new function call and removing any previous calls that
# are rendered obselete.
# Note: changes_dict is a chain of ordered dicts
def AddFunctionCallTokensToChangesDict(function_tokens: List[str], changes_dict: OrderedDict):
    CheckType(function_tokens, 'function_tokens', list, str)
    CheckType(changes_dict, 'changes_dict', OrderedDict)
    current_dict = changes_dict
    function_name = function_tokens[0]
    num_params_for_match = kFunctionInfoMap[function_name]['NumParamsForMatch']
    for i, current_token in enumerate(function_tokens):
        # Final token, maps to None
        if ((i + 1) == len(function_tokens)):
            current_dict[current_token] = None
        # At number of params for match, overwrite any existing function here
        elif (i == num_params_for_match):
            current_dict[current_token] = OrderedDict()
        # Regardless of what happened, step one level deeper (ensure there is a level deeper first)
        if (current_token not in current_dict):
            current_dict[current_token] = OrderedDict()
        current_dict = current_dict[current_token]
# End AddFunctionCallTokensToChangesDict

# Same as above, but takes the function call as a single string
def AddFunctionCallStringToChangesDict(function_call_string: str, changes_dict: OrderedDict):
    CheckType(function_call_string, 'function_call_string', str)
    CheckType(changes_dict, 'changes_dict', OrderedDict)
    AddFunctionCallTokensToChangesDict(shlex.split(function_call_string), changes_dict)
# End AddFunctionCallStringToChangesDict

# Returns a chain of OrderedDicts representing the given profile's changes file
def ParseProfileChanges(profile_name) -> OrderedDict:
    changes_dict = OrderedDict()
    changes_lines = file_helper.ReadFile(profile.GetProfileChangesFullpath(profile_name),
                                         strip=True)
    for function_call_string in changes_lines:
        AddFunctionCallStringToChangesDict(function_call_string, changes_dict)
    return changes_dict
# End ParseProfileChanges

# Returns list of lists of function tokens, for example:
# [['adjust_currency_tier', 'Chromatic Orb', '1'],
#  ['hide_uniques_above_tier', '3']]
def ConvertChangesDictToFunctionTokenListListRec(
        changes_dict: OrderedDict, current_prefix_list: List[str] = []) -> List[List[str]]:
    CheckType(changes_dict, 'changes_dict', OrderedDict)
    CheckType(current_prefix_list, 'current_prefix_list', list, str)
    result_list = []
    for param, subdict in changes_dict.items():
        new_prefix_list = current_prefix_list + [param]
        if (subdict == None):
            result_list.append(new_prefix_list)
        else:
            result_list.extend(ConvertChangesDictToFunctionTokenListListRec(
                    subdict, new_prefix_list))
    return result_list
# End ConvertChangesDictToFunctionListRec

# Returns list of lists of function call strings, for example:
# ['adjust_currency_tier "Chromatic Orb" 1',
#  'hide_uniques_above_tier 3']
def ConvertChangesDictToFunctionCallStringList(changes_dict: OrderedDict) -> List[str]:
    CheckType(changes_dict, 'changes_dict', OrderedDict)
    # Get list of lists of function tokens from recursive function above
    token_lists = ConvertChangesDictToFunctionTokenListListRec(changes_dict)
    function_list = []
    for token_list in token_lists:
        function_list.append(JoinParamsDoubleQuotes(token_list))
    return function_list
# End ConvertChangesDictToFunctionList

# Adds the given change to the given profile's changes file, removing any previous changes that this
# function call renders obselete.
def AddChangeToProfile(new_function_name: str,
                           new_function_params: List[str],
                           profile_name: str,):
    CheckType(new_function_name, 'new_function_name', str)
    CheckType(new_function_params, 'new_function_params', list, str)
    CheckType(profile_name, 'profile_name', str)
    # Generate changes_dict by parsing changes file and adding new function call
    changes_path = profile.GetProfileChangesFullpath(profile_name)
    changes_dict = ParseProfileChanges(profile_name)
    AddFunctionCallTokensToChangesDict([new_function_name] + new_function_params, changes_dict)
    # Write changes_dict to changes file
    changes_list = ConvertChangesDictToFunctionCallStringList(changes_dict)
    file_helper.WriteToFile(changes_list, changes_path)
# End AddChangeToProfile
