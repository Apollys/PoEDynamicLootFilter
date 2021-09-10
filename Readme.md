# PoE Dynamic Loot Filter

Tool to Modify your Loot Filter seamlessly while playing Path of Exile

- - -

### Cody To-Do
 - Fix test suite to work with new profile system
 - Create a more thorough set of tests to cover everything in the backend_cli
   - Examples: make sure filter is saved whenever a change is made, make sure things go to the
     right tier/status by re-reading the file, make sure it doesn't save on batch of getters, etc

- - -

### Feature Wish List
 - [x] Move currency from one tier to another
 - [x] Show/hide whole currency tier
 - [x] Chaos recipe - show/hide by item slot
 - [x] Hide maps below tier
 - [x] Show/hide flasks by type
 - [x] Save profile data - persistent changes with redownloaded filter
 - [x] Manipulate unique item visibility
 - [ ] Simulate - find rule matching item - partially complete
 - [x] Set Gem min quality
 - [ ] Set Flask min quality
 - [ ] Set RGB item max size
 - [ ] Set Blight Oil min tier
 - [ ] Profile rework: frontend
 - [x] Profile rework: backend (separate all profile config data from python code)
   - Formatting of profile file could probably be improved
 - [x] Add user-defined custom rules (user writes custom rules in a text file,
   whenever the filter is imported those rules are automatically added.
   Useful for adding any rule FilterBlade doesn't support, like "3 sockets, at least 2 blues"

- - -

### Frontend-Backend API Specification

The AHK frontend calls the Python backend via:
```
> python3 backend_cli.py <profile_name> <function_name> <function_parameters...>
```
The Python backend communicates return values to AHK by writing them to the file `backend_cli.output`.

See [`backend_cli.py`](https://github.com/Apollys/PoEDynamicLootFilter/blob/master/backend_cli.py) for the detailed documentation of all available function calls.

**Currently Supported Functions:**
  - `run_batch`
    - TODO: make input filepath first argument (maybe?)
  - `undo_last_change`
  - `import_downloaded_filter <optional keyword: "only_if_missing">`
  - `get_rule_matching_item`
  - `set_rule_visibility <type_tag: str> <tier_tag: str> <visibility: {show, hide, disable}>`
  - `set_currency_tier <currency_name: str> <tier: int>`
  - `adjust_currency_tier <currency_name: str> <tier_delta: int>`
  - `get_all_currency_tiers`
  - `set_currency_tier_visibility`
  - `get_currency_tier_visibility`
  - `get_all_unique_tier_visibilities`
  - `set_hide_uniques_above_tier`
  - `get_hide_uniques_above_tier`
  - *Recenty added:* `set_gem_min_quality <tier: int in [1, 20]>`
  - *Recenty added:* `get_gem_min_quality`
  - `set_hide_currency_above_tier`
  - `get_hide_currency_above_tier`
  - `set_hide_maps_below_tier <tier: int>`
  - `get_hide_maps_below_tier`
  - `set_flask_rule_enabled_for <base_type: str> <enable_flag: int>`
  - `is_flask_rule_enabled_for <base_type: str>`
  - `get_all_enabled_flask_types` \*
  - `set_chaos_recipe_enabled_for <item_slot: str> <enable_flag: int>`
  - `is_chaos_recipe_enabled_for <item_slot: str>`
  - `get_all_chaos_recipe_statuses`

**Functions To Implement**
 - Simulate - find rule matching item

\* Can this be changed to something more like the get_all_currency_tiers where it returns every flask type with <flask name>;<int: active>? Would be a lot easier for me
 
