# PoEDynamicLootFilter

Tool to Modify your Loot Filter seamlessly while playing Path of Exile

- - -

### Feature Wish List
 - [x] Move currency from one tier to another
 - [x] Show/hide whole currency tier
 - [x] Chaos recipe - show/hide by item slot
 - [x] Hide maps below tier
 - [ ] Show/hide flasks by type
 - [ ] Save profile data - persistent changes with redownloaded filter

- - -

### Frontend-Backend API Specification

The AHK frontend calls the Python backend via:
```
> python3 backend_cli.py <function_name> <function_parameters...>
```
The Python backend communicates return values to AHK by writing them to the file `backend_cli.output`.

See [`backend_cli.py`](https://github.com/Apollys/PoEDynamicLootFilter/blob/master/backend_cli.py) for the detailed documentation of all available function calls.

**Currently Supported Functions:**
  - `batch_process`
    - Processes a sequence of functions specified in the file `backend_cli.input`
    - Each line of the file is one function call, formatted as `<function_name> <function_params...>` (i.e. just like the cli function call but without `python3 backend_cli.py `
    - Ouput is separated by the single-character line `@` placed after the output of each function call in `backend_cli.output`
  - `import_downloaded_filter`
  - `set_currency_tier <currency_name: str> <tier: int>`
  - `adjust_currency_tier <currency_name: str> <tier_delta: int>`
  - `get_all_currency_tiers`
  - `set_currency_tier_visibility`
  - `get_currency_tier_visibility`
  - `set_hide_currency_above_tier`
  - `get_hide_currency_above_tier`
  - `set_hide_map_below_tier <tier: int>`
  - `get_hide_map_below_tier`
  - `set_chaos_recipe_enabled_for <item_slot: str> <enable_flag: int>`
  - `is_chaos_recipe_enabled_for <item_slot: str>`
  - `get_all_chaos_recipe_statuses`

**Functions To Implement**
 - `undo_last_change`
   - Initial implementation - "profile" saved as a text file of cli function calls, one per line
   - `undo_last_change` would remove the last line from the profile, then re-import downloaded filter and apply changes from profile text file

