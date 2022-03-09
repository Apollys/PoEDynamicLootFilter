# PoE Dynamic Loot Filter

Tool to Modify your Loot Filter seamlessly while playing Path of Exile

- - -

### Syntax for backend command-line interface calls

```
> python3 backend_cli.py <function_name> <function_parameters...> <profile_name (if required)>
```

The `profile_name` parameter is required in all cases except for:
 - `get_all_profile_names`
 - `set_active_profile`

- - -

### To-Do
 - [ ] Add first-time setup support
   - [x] Add backend function `is_first_launch`
   - [ ] If yes, prompt user for profile name, create profile,
     explain how to configure options and add custom rules
 - [ ] Implement Create Profile button in UI
 - [x] Implement UI display error messages on important failures
   - [x] Failed to import filter
   - [x] Or more generally, always report status of last action
 - [x] ~~Explicitly check for presence of downloaded filter,
       give more clear error message if missing~~
	   This was already done, the UI just needs to propogate the error
 - [ ] Skip unrecognized commands in Profile.changes file (with warning)
   - Likely cause is depracated feature from version update
   - Better not to fail in this case
 - [ ] Test suite: Change `CHECK` macro to `CHECK_EQ`, etc
 - [ ] (Low priority) fix not parsing tags for custom rules
 - [ ] Refactor frontend AHK script
   - [x] Reorder and organize build GUI code
   - [ ] Write helper functions to make GUI construction more concise.
         For example, combining setting font with creating an item
   - [ ] Resolve minor questions in AHK script (ctr-f TODO)
   - [ ] Refactor all of the code to use a functional style
 - [ ] Fix backend function get_rule_matching_item
 - [x] Add tests for newly added featuers:
   - [x] Stacked currency
   - [x] Essences
   - [x] Div cards
   - [x] Unique maps
 - [x] Stacked Currency:
   - [x] Change 2, 4, 8 to 2, 4, 6 (8 doesn't drop naturally)
   - [x] Make currency stack tiers consistent with single currency tiers on import
 - [x] ~~Add Harbinger Shard, Horizon Shard, Chaos Shard to tiering~~
   - No longer appliccable, as v2 shows all currency basetypes
 - [x] Add support for essences
 - [x] Add support for div cards
 - [x] Add support for unique maps
 - [x] Make backend return exit codes so front end can detect errors
 - [x] UI Redesign

- - -

### Feature Wish List
 - [ ] First time setup documentation
 - [ ] First time setup workflow in UI
 - [x] Add support for essences
 - [x] Add support for div cards
 - [x] Add support for unique maps
 - [x] Update flask rules - one for high ilvl (85+) and one for all ilvls
 - [x] Move currency from one tier to another
 - [x] Show/hide whole currency tier
 - [x] Chaos recipe - show/hide by item slot
 - [x] Hide maps below tier
 - [x] Show/hide flasks by type
 - [x] Save profile data - persistent changes with redownloaded filter
 - [x] Manipulate unique item visibility
 - [x] Simulate - find rule matching item
   - All done except socket colors
 - [x] Set Gem min quality
 - [x] Set Flask min quality
 - [x] Set RGB item max size
 - [x] Set Blight Oil min tier
 - [x] Profile rework
   - Formatting of profile file could probably be improved
 - [x] Add user-defined custom rules (user writes custom rules in a text file,
   whenever the filter is imported those rules are automatically added.
   Useful for adding any rule FilterBlade doesn't support, like "3 sockets, at least 2 blues"

- - -

### Frontend-Backend API Specification

The AHK frontend calls the Python backend via:
```
> python3 backend_cli.py <function_name> <function_parameters...> <profile_name (if required)>
```
The Python backend communicates output values to AHK by writing them to the file
`backend_cli.output`.  It writes an exit code to `backend_cli.exit_code`: `-1` indicates
in-progress, `0` indicates exit success, and `1` indicates exit with error
(`backend_cli.log` contains error details).

See [`backend_cli.py`](https://github.com/Apollys/PoEDynamicLootFilter/blob/master/backend_cli.py)
for the detailed documentation of all available function calls.

**Currently Supported Functions:**
  - `is_first_launch`
  - `get_all_profile_names`
  - `create_new_profile <new_profile_name>`
  - `set_active_profile`
  - `import_downloaded_filter <optional keyword: "only_if_missing">`
  - `run_batch`
  - `get_rule_matching_item`
  - `set_rule_visibility <type_tag: str> <tier_tag: str> <visibility: {show, hide, disable}>`
  - *New/Updated*: `set_currency_to_tier <currency_name: str> <tier: int>`
  - *New/Updated*: `get_all_currency_tiers`
  - *New/Updated*: `set_currency_tier_min_visible_stack_size <tier: int> <visible_flag: int>`
  - *New/Updated*: `get_currency_tier_min_visible_stack_size <tier: int>`
  - (For test suite use: `get_tier_of_currency <currency_name: str>`)
  - *All Other Currency Functions Removed*, notably:
    - `set_/get_hide_currency_above_tier`
    - `set_/get_currency_tier_visibility`
  - *New*: `set_archnemesis_mod_tier <archnemesis_mod_name: str> <tier: int>`
  - *New*: `get_all_archnemesis_mod_tiers`
  - *New*: `get_all_essence_tier_visibilities`
  - *New*: `set_hide_essences_above_tier <tier: int>`
  - *New*: `get_hide_essences_above_tier`
  - *New*: `get_all_div_card_tier_visibilities`
  - *New*: `set_hide_div_cards_above_tier <tier: int>`
  - *New*: `get_hide_div_cards_above_tier`
  - *Renamed*: `get_all_unique_item_tier_visibilities`
  - *Renamed*: `set_hide_unique_items_above_tier <tier: int>`
  - *Renamed*: `get_hide_unique_items_above_tier`
  - *New*: `get_all_unique_map_tier_visibilities`
  - *New*: `set_hide_unique_maps_above_tier <tier: int>`
  - *New*: `get_hide_unique_maps_above_tier`
  - `set_lowest_visible_oil <oil_name: str>`
  - `get_lowest_visible_oil`
  - `set_gem_min_quality <quality: int in [1, 20]>`
  - `get_gem_min_quality`
  - `set_flask_min_quality <quality: int in [1, 20]>`
  - `get_flask_min_quality`
  - `set_hide_maps_below_tier <tier: int>`
  - `get_hide_maps_below_tier`
  - `set_flask_visibility <base_type: str> <visibility_flag: int>`
  - `set_high_ilvl_flask_visibility <base_type: str> <visibility_flag: int>`
  - `get_flask_visibility <base_type: str>`
  - `get_all_flask_visibilities`
  - `set_rgb_item_max_size <size: {none, small, medium, large}>`
  - `get_rgb_item_max_size`
  - `set_chaos_recipe_enabled_for <item_slot: str> <enable_flag: int>`
  - `is_chaos_recipe_enabled_for <item_slot: str>`
  - `get_all_chaos_recipe_statuses`

