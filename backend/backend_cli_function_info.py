# Map of function name -> dictionary of properties indexed by the following string keywords:
# - NumParamsOptions: List[int] (excludes function name and profile param)
# - HasProfileParam: bool
# - ModifiesFilter: bool
# - NumParamsForMatch: int, only used for functions that modify the filter. It
#   Tells how many parameters need to be the same for two functions of this name to be
#   reducible to a single function in the profile changes file.  For example:
#     > adjust_currency_tier "Chromatic Orb" +1
#     > adjust_currency_tier "Chromatic Orb" +1
#   is reducible to
#     > adjust_currency_tier "Chromatic Orb" +2
#   so this value would be 1 for 'adjust_currency_tier'.
kFunctionInfoMap = {
    'is_first_launch' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    'check_for_update': {
        'NumParamsOptions' : [0],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    # General config
    'set_hotkey' : {
        'NumParamsOptions' : [2],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    'get_all_hotkeys' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    # Profiles
    'get_all_profile_names' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    'create_new_profile' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    'rename_profile' : {
        'NumParamsOptions' : [2],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    'delete_profile' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    'set_active_profile' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : False,
        'ModifiesFilter' : False,
    },
    # Check Filters Exist
    'check_filters_exist' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Import and Reload
    # These are *not* considered as mutator functions,
    # because they do not contribute to Profile.changes.
    'import_downloaded_filter' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'load_input_filter' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Miscellaneous
    'run_batch' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_rule_matching_item' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'set_rule_visibility' : {
        'NumParamsOptions' : [3],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 2,
    },
    # Currency
    'set_currency_to_tier' : {
        'NumParamsOptions' : [2],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 1,
    },
    'get_tier_of_currency' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_all_currency_tiers' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'set_currency_tier_min_visible_stack_size' : {
        'NumParamsOptions' : [2],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 1,
    },
    'get_currency_tier_min_visible_stack_size' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_all_currency_tier_min_visible_stack_sizes' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Splinters
    'set_splinter_min_visible_stack_size' : {
        'NumParamsOptions' : [2],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 1,
    },
    'get_splinter_min_visible_stack_size' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_all_splinter_min_visible_stack_sizes' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Essences
    'get_all_essence_tier_visibilities' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'set_hide_essences_above_tier' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_hide_essences_above_tier' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Divination Cards
    'get_all_div_card_tier_visibilities' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'set_hide_div_cards_above_tier' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_hide_div_cards_above_tier' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Unique Items
    'get_all_unique_item_tier_visibilities' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'set_hide_unique_items_above_tier' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_hide_unique_items_above_tier' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Unique Maps
    'get_all_unique_map_tier_visibilities' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'set_hide_unique_maps_above_tier' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_hide_unique_maps_above_tier' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Oils
    'set_lowest_visible_oil' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_lowest_visible_oil' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Quality Gems
    'set_gem_min_quality' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_gem_min_quality' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Quality Flasks
    'set_flask_min_quality' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_flask_min_quality' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Hide Maps Below Tier
    'set_hide_maps_below_tier' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_hide_maps_below_tier' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Generic BaseTypes
    'set_basetype_visibility' : {
        'NumParamsOptions' : [2, 3],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 1,
    },
    'get_basetype_visibility' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_all_visible_basetypes' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Flasks Types
    'set_flask_visibility' : {
        'NumParamsOptions' : [2, 3],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 1,
    },
    'get_flask_visibility' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_all_visible_flasks' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Socket Rules
    'add_remove_socket_rule' : {
        'NumParamsOptions' : [2, 3],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 2,
    },
    'get_all_added_socket_rules' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # RGB Items
    'set_rgb_item_max_size' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 0,
    },
    'get_rgb_item_max_size' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    # Chaos Recipe
    'set_chaos_recipe_enabled_for' : {
        'NumParamsOptions' : [2],
        'HasProfileParam' : True,
        'ModifiesFilter' : True,
        'NumParamsForMatch' : 1,
    },
    'is_chaos_recipe_enabled_for' : {
        'NumParamsOptions' : [1],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
    'get_all_chaos_recipe_statuses' : {
        'NumParamsOptions' : [0],
        'HasProfileParam' : True,
        'ModifiesFilter' : False,
    },
}
