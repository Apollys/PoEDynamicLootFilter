# PoE Dynamic Loot Filter

Tool to Modify your Loot Filter seamlessly while playing Path of Exile

- - -

### Updated syntax for backend command-line interface calls

```
> python3 backend_cli.py <function_name> <function_parameters...> <profile_name (if required)>
```

The `profile_name` parameter is required in all cases except for:
 - `get_all_profile_names`
 - `set_active_profile`

- - -

### To-Do
 - Stacked Currency:
   - Goal: generate stacked rules for 2, 4, 8 of every currency tier
   - Parse full filter, comment out Neversink's stack rules
   - Use the format of Neversink's stack rules to generate DLF added stack rules
   - Alternate initial implementation: just copy the base currency rules, make icons bigger
 - Flasks:
   - Add `set_high_ilvl_flask_visibility <basetype>` function

- - -

### Feature Wish List
 - [ ] Update flask rules - one for high ilvl (85+) and one for all ilvls
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
The Python backend communicates return values to AHK by writing them to the file
`backend_cli.output`.

See [`backend_cli.py`](https://github.com/Apollys/PoEDynamicLootFilter/blob/master/backend_cli.py)
for the detailed documentation of all available function calls.

**Currently Supported Functions:**
  - `get_all_profile_names`
  - `create_new_profile <new_profile_name>`
  - `set_active_profile`
  - `import_downloaded_filter <optional keyword: "only_if_missing">`
  - `run_batch`
  - `get_rule_matching_item`
  - `set_rule_visibility <type_tag: str> <tier_tag: str> <visibility: {show, hide, disable}>`
  - `set_currency_tier <currency_name: str> <tier: int>`
  - \[removed] `adjust_currency_tier <currency_name: str> <tier_delta: int>`
  - `get_currency_tier <currency_name: str>`
  - `get_all_currency_tiers`
  - `set_currency_tier_visibility <tier: int or tier_tag: str> <visible_flag: int>`
  - `get_currency_tier_visibility <tier: int or tier_tag: str>`
  - `set_hide_currency_above_tier <tier: int>`
  - `get_hide_currency_above_tier`
  - *New*: `set_currency_min_visible_stack_size <tier: int or string> <stack_size: int or "hide_all">`
  - `set_lowest_visible_oil <oil_name: str>`
  - `get_lowest_visible_oil`
  - `get_all_unique_tier_visibilities`
  - `set_hide_uniques_above_tier <tier: int>`
  - `get_hide_uniques_above_tier`
  - `set_gem_min_quality <quality: int in [1, 20]>`
  - `get_gem_min_quality`
  - `set_flask_min_quality <quality: int in [1, 20]>`
  - `get_flask_min_quality`
  - `set_hide_maps_below_tier <tier: int>`
  - `get_hide_maps_below_tier`
  - `set_flask_visibility <base_type: str> <visibility_flag: int>`
  - *New* `set_high_ilvl_flask_visibility <base_type: str> <visibility_flag: int>`
  - `get_flask_visibility <base_type: str>`
  - `get_all_flask_visibilities`
  - `set_rgb_item_max_size <size: {none, small, medium, large}>`
  - `get_rgb_item_max_size`
  - `set_chaos_recipe_enabled_for <item_slot: str> <enable_flag: int>`
  - `is_chaos_recipe_enabled_for <item_slot: str>`
  - `get_all_chaos_recipe_statuses`

