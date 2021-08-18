# PoEDynamicLootFilter

Tool to Modify your Loot Filter seamlessly while playing Path of Exile

- - -

### Feature Wish List
 - [x] Move currency from one tier to another
 - [x] Show/hide whole currency tier
 - [ ] Chaos recipe - show/hide by item slot
 - [ ] Hide maps below tier
 - [ ] Show/hide flasks by type
 - [ ] Save profile data - persistent changes with redownloaded filter

- - -

### Todo Checklists

**Frontend (AHK)**
 - [x] Verify that we can call Python scripts from within AHK
 - [ ] Add Backend requirements

**Backend (Python)**
 - [x] Move currency from one tier to another
 - [x] Show/Hide/Disable any rule
 - [ ] Add and modify chaos recipe rules, assuming filter doesn't start out with them
 - [ ] Set size for any rule
 - [ ] Hide all maps below specified tier
 - [ ] Add "profiles" - track and encode any changes made to the current filter, so that changes can be made to the filter in FilterBlade, the filter can be redownloaded, and all PoEDynamicLootFilter modifications can be immediately applied to the newly downloaded filter 

- - -

### Frontend-Backend API Specification

The AHK frontend calls the Python backend via:
```
> python3 backend_cli.py <function_name> <function_parameters...>
```

The Python backend communicates return values to AHK by writing them to the file `backend_cli.output`.

**Currently Supported Functions:**
 - `adjust_currency_tier <currency_name> <tier_delta: int> -> None`  (-> indicates return value) 

**Functions To Implement**
 - `set_currency_tier <currency_name> <tier: int> -> None`
 - `get_currency_tiers (optional: <currency_name>) -> all (or specified) currency tiers in current filter`\*
     + Output format: one line `"<currency_name>";<tier: int>` for each currency type
 - `set_rare_status <rare_type: string> <status: bool/int> -> None`
 - `get_rare_status (optional : <rare_type>) -> all (or specified) chaos rare statuses in current filter`
     + Output format should be `"<Rare Type>";<status>` with one entry per line. Current Rare types are Body, Wep, Boot, Glove, Helm, Amu, Ring, Belt (can be changed easily)\*
 - Maybe in the future `update_filter -> None` reads a large number of changes from a fixed text file and performs them all

\*Confused about parameter and return value, can you double check that you wrote this correctly?  What would `get_currency_tiers "Orb of Alchemy"` return?

\*\*For chaos recipe item slots, let's use the categories listed in `consts.py`:
```python
kChaosRecipeCategories = ['weapons',
                          'body_armours',
                          'helmets',
                          'gloves',
                          'boots',
                          'amulets',
                          'rings',
                          'belts']
```
