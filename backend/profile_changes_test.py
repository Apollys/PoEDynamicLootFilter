import profile_changes

from collections import OrderedDict
import shlex
from typing import List

import file_helper
import profile
import test_consts
import test_helper
from test_assertions import AssertEqual, AssertFailure
from type_checker import CheckType

kProfileChangesTestCaseInput = [
    'set_currency_to_tier "Chromatic Orb" 5',
    'set_hide_maps_below_tier 11',
    'set_basetype_visibility "Hubris Circlet" 1 1',
    'set_currency_to_tier "Chromatic Orb" 6',
    'set_hide_maps_below_tier 16',
    'set_basetype_visibility "Hubris Circlet" 0',
    'set_currency_to_tier "Chromatic Orb" 7',
    'set_hide_maps_below_tier 12',
    'set_basetype_visibility "Hubris Circlet" 1 0']

kProfileChangesTestCaseFinal = kProfileChangesTestCaseInput[-3:]

# ============================= Helper Functions =============================

# Creates a chain of OrderedDict->OrderedDict->...->None from a single function call string
def CreateOrderedDictChain(function_call_string: str) -> OrderedDict:
    CheckType(function_call_string, 'function_call_string', str)
    tokens = shlex.split(function_call_string)
    root_ordered_dict = OrderedDict()
    current_ordered_dict = root_ordered_dict
    for token in tokens[:-1]:
        current_ordered_dict[token] = OrderedDict()
        current_ordered_dict = current_ordered_dict[token]
    current_ordered_dict[tokens[-1]] = None
    return root_ordered_dict

# Creates an OrderedDict of OrderedDict chains from a list of function call strings,
# assuming the function names are all distinct.
def CreateOrderedDictChains(function_call_strings: List[str]) -> OrderedDict:
    CheckType(function_call_strings, 'function_call_strings', list, str)
    ordered_dict = OrderedDict()
    for function_call_string in function_call_strings:
        ordered_dict.update(CreateOrderedDictChain(function_call_string))
    return ordered_dict

def TestCreateOrderedDictChains():
    function_call_strings = [
        'set_currency_to_tier "Chromatic Orb" 5',
        'set_hide_maps_below_tier 11'
    ]
    expected_ordered_dict = OrderedDict([
        ('set_currency_to_tier', OrderedDict([('Chromatic Orb', OrderedDict([('5', None)]))])),
        ('set_hide_maps_below_tier', OrderedDict([('11', None)]))])
    AssertEqual(CreateOrderedDictChains(function_call_strings), expected_ordered_dict)
    print('TestCreateOrderedDictChain passed!')

# =================================== Tests ===================================

def TestJoinParamsDoubleQuotes():
    tokens = ["The", "quick brown", "fox's", "fur", "is soft."]
    expected_joined_string = '''The "quick brown" "fox's" fur "is soft."'''
    AssertEqual(profile_changes.JoinParamsDoubleQuotes(tokens), expected_joined_string)
    print('TestJoinParamsDoubleQuotes passed!')

def TestNonClashingAddFunctionToChangesDict():
    function_call_strings = [
        'set_currency_to_tier "Chromatic Orb" 5',
        'set_hide_maps_below_tier 11',
        'set_lowest_visible_oil  "Azure Oil"']
    expected_changes_dict = CreateOrderedDictChains(function_call_strings)
    changes_dict = OrderedDict()
    for function_call_string in function_call_strings:
        profile_changes.AddFunctionCallStringToChangesDict(function_call_string, changes_dict)
    AssertEqual(changes_dict, expected_changes_dict)
    print('TestNonClashingAddFunctionToChangesDict passed!')

# Tests AddFunctionCallTokensToChangesDict and AddFunctionCallStringToChangesDict.
# The latter delegates to the former, so we expect their correctness to be tightly coupled.
def TestAddFunctionToChangesDict():
    expected_changes_dict = CreateOrderedDictChains(kProfileChangesTestCaseFinal)
    changes_dict_strings = OrderedDict()
    changes_dict_tokens = OrderedDict()
    for function_call_string in kProfileChangesTestCaseInput:
        profile_changes.AddFunctionCallStringToChangesDict(
                function_call_string, changes_dict_strings)
        function_name, *function_params = shlex.split(function_call_string)
        profile_changes.AddFunctionCallTokensToChangesDict(
                [function_name] + function_params, changes_dict_tokens)
    AssertEqual(changes_dict_tokens, expected_changes_dict)
    AssertEqual(changes_dict_strings, expected_changes_dict)
    print('TestAddFunctionToChangesDict passed!')

def TestParseChangesFile():
    test_helper.SetUp()
    changes_path = profile.GetProfileChangesFullpath(test_consts.kTestProfileName)
    file_helper.WriteToFile(kProfileChangesTestCaseInput, changes_path)
    parsed_changes_dict = profile_changes.ParseProfileChanges(test_consts.kTestProfileName)
    # Use previous test as expected result, since it's already passed by now
    expected_changes_dict = OrderedDict()
    for function_call_string in kProfileChangesTestCaseInput:
        profile_changes.AddFunctionCallStringToChangesDict(
                function_call_string, expected_changes_dict)
    AssertEqual(parsed_changes_dict, expected_changes_dict)
    print('TestParseChangesFile passed!')

# Tests ConvertChangesDictToFunctionListRec and ConvertChangesDictToFunctionCallStringList.
# The latter delegates to the former, so we expect their correctness to be tightly coupled.
def TestConvertChangesDictTo():
    # Generate input changes_dict
    changes_dict = OrderedDict()
    for function_call_string in kProfileChangesTestCaseInput:
        profile_changes.AddFunctionCallStringToChangesDict(function_call_string, changes_dict)
    # Test ConvertChangesDictToFunctionListRec
    expected_function_token_list_list = [shlex.split(s) for s in kProfileChangesTestCaseFinal]
    AssertEqual(profile_changes.ConvertChangesDictToFunctionTokenListListRec(changes_dict),
                expected_function_token_list_list)
    # Test ConvertChangesDictToFunctionCallStringList
    AssertEqual(profile_changes.ConvertChangesDictToFunctionCallStringList(changes_dict),
                kProfileChangesTestCaseFinal)
    print('TestConvertChangesDictTo passed!')

def TestAddChangeToChangesFile():
    test_helper.SetUp()
    expected_changes_dict = OrderedDict()
    for function_call_string in kProfileChangesTestCaseInput:
        function_name, *function_params = shlex.split(function_call_string)
        profile_changes.AddChangeToProfile(
                function_name, function_params, test_consts.kTestProfileName)
        # Update expected_changes_dict with matching change
        profile_changes.AddFunctionCallStringToChangesDict(
                function_call_string, expected_changes_dict)
    # Parse final result to check if it's correct
    parsed_changes_dict = profile_changes.ParseProfileChanges(test_consts.kTestProfileName)
    AssertEqual(parsed_changes_dict, expected_changes_dict)
    print('TestAddChangeToChangesFile passed!')

def main():
    TestCreateOrderedDictChains()
    TestJoinParamsDoubleQuotes()
    TestNonClashingAddFunctionToChangesDict()
    TestAddFunctionToChangesDict()
    TestParseChangesFile()
    TestConvertChangesDictTo()
    TestAddChangeToChangesFile()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()