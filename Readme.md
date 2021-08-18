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

See [`backend_cli.py`](https://github.com/Apollys/PoEDynamicLootFilter/blob/master/backend_cli.py) for the detailed documentation of all available function calls.

**Currently Supported Functions:**
  - `adjust_currency_tier <currency_name: str> <tier_delta: int>`
    - Moves a given currency type by a relative tier_delta
    - Output: None
    - Example: `> python3 backend_cli.py adjust_currency_tier "Chromatic Orb" -2`
  - set_currency_tier <currency_name: str> <tier: int>
    - Moves the given currency type to the specified tier
    - Output: None
    - Example: > python3 backend_cli.py set_currency_tier "Chromatic Orb" 5
  - `get_currency_tiers`
    - Output: newline-separated sequence of `<currency_name: str>;<tier: int>`, one per currency type
    - Example: `> python3 backend_cli.py get_currency_tiers`

**Functions To Implement**
 - `batch_process`
   - Processes a sequence of functions specified in the file `backend_cli.input`
   - Each line of the file is one function call, formatted as `<function_name> <function_params...>` (i.e. just like the cli function call but without `python3 backend_cli.py `
   - Ouput is separated by the line `# [end_function_output]` placed after the output of each function call in `backend_cli.output`
 - XXX`set_rare_status <rare_type: string> <status: bool/int> -> None`XXX Temporary hold, potentially unnecessary
 - `get_rare_status -> all chaos rare statuses in current filter`
     + Output format should be `<Rare Type>;<status>` with one entry per line. Rare Types in `consts.py`
 - `update_filter (optional <item :Rare/Currency>)-> None` reads a large number of changes from a fixed text file and performs them all

\*\*For chaos recipe item slots, let's use the categories listed in `consts.py`:
```python
kChaosRecipeCategories = ['Weapons',
                          'Body Armours',
                          'Helmets',
                          'Gloves',
                          'Boots',
                          'Amulets',
                          'Rings',
                          'Belts']
```
These are the exact item slot names used in the drop filter syntax, except for Weapons which I added as a blanket term.
