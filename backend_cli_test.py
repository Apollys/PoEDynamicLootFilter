import os

import profile
import test_consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse
import test_helper
from type_checker import CheckType

# Expected input form: "set_min_gem_quality 18" (profile name omitted)
def CallBackendCli(function_call: str, profile_name: str or None = None):
    CheckType(function_call, 'function_call', str)
    CheckType(profile_name, 'profile_name', (str, type(None)))
    full_command = 'python backend_cli.py ' + function_call
    if (profile_name != None):
        full_command += ' ' + test_consts.kTestProfileName
    print('Running: {}'.format(full_command))
    return_value = os.system(full_command)
    AssertEqual(return_value, 0)
# End CallBackendCli

# Not included:
#  - is_first_launch
#  - get_all_profile_names
#  - create/rename/delete/set_active_profile
#  - import/reload filter
#  - run_batch
#  - get_rule_matching_item
kTestBatchString = \
'''check_filters_exist
set_rule_visibility "jewels->abyss" highrare disable
set_rule_visibility "jewels->abyss" highrare hide
set_currency_to_tier "Chromatic Orb" 2
get_tier_of_currency "Chromatic Orb"
get_all_currency_tiers
set_currency_tier_min_visible_stack_size 2 4
get_currency_tier_min_visible_stack_size 2
set_currency_tier_min_visible_stack_size twisdom 1
get_currency_tier_min_visible_stack_size twisdom
get_all_essence_tier_visibilities
set_hide_essences_above_tier 1
get_hide_essences_above_tier
get_all_div_card_tier_visibilities
set_hide_div_cards_above_tier 1
get_hide_div_cards_above_tier
get_all_unique_item_tier_visibilities
set_hide_unique_items_above_tier 1
get_hide_unique_items_above_tier
get_all_unique_map_tier_visibilities
set_hide_unique_maps_above_tier 1
get_hide_unique_maps_above_tier
set_lowest_visible_oil "Golden Oil"
get_lowest_visible_oil
set_gem_min_quality 18
get_gem_min_quality
set_flask_min_quality 11
get_flask_min_quality
set_hide_maps_below_tier 13
get_hide_maps_below_tier
set_basetype_visibility "Hubris Circlet" 1 0
set_basetype_visibility "Hubris Circlet" 1 1
get_basetype_visibility "Hubris Circlet"
get_all_visible_basetypes
set_flask_visibility "Quicksilver Flask" 1
set_flask_visibility "Quicksilver Flask" 0
set_high_ilvl_flask_visibility "Quicksilver Flask" 1
get_flask_visibility "Quicksilver Flask"
get_all_flask_visibilities
set_rgb_item_max_size small
get_rgb_item_max_size
set_chaos_recipe_enabled_for "Weapons" 0
set_chaos_recipe_enabled_for "Body Armours" 0
set_chaos_recipe_enabled_for "Helmets" 1
set_chaos_recipe_enabled_for "Gloves" 1
set_chaos_recipe_enabled_for "Boots" 1
set_chaos_recipe_enabled_for "Rings" 0
set_chaos_recipe_enabled_for "Amulets" 1
set_chaos_recipe_enabled_for "Belts" 0
is_chaos_recipe_enabled_for "Weapons"
get_all_chaos_recipe_statuses'''

# Just a simple test to see if the functions can run without error;
# doesn't verify output is correct.
def SimpleTest():
    test_helper.SetUp(create_profile=False)
    profile_name = test_consts.kTestProfileName
    other_profile_name = test_consts.kOtherTestProfileName
    CallBackendCli('is_first_launch')
    CallBackendCli('get_all_profile_names')
    # TODO: need to write config values to backend_cli.input to use this function
    # CallBackendCli('create_new_profile {}'.format(profile_name))
    profile.CreateNewProfile(profile_name, test_consts.kTestProfileConfigValues)
    CallBackendCli('rename_profile {} {}'.format(profile_name, other_profile_name))
    CallBackendCli('delete_profile {}'.format(other_profile_name))
    profile.CreateNewProfile(profile_name, test_consts.kTestProfileConfigValues)
    profile.CreateNewProfile(other_profile_name, test_consts.kTestProfileConfigValues)
    CallBackendCli('set_active_profile {}'.format(profile_name))
    profile.DeleteProfile(other_profile_name)
    CallBackendCli('import_downloaded_filter', profile_name)
    CallBackendCli('reload_input_filter', profile_name)
    for function_call_line in kTestBatchString.split('\n'):
        CallBackendCli(function_call_line, profile_name)
    print('SimpleTest passed!')

def main():
    SimpleTest()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()