# PoEDynamicLootFilter

Tool to Modify your Loot Filter seamlessly while playing Path of Exile

- - -

### Recent Updates

Python backend CLI now added, only supports a single function currently.  See backend_cli.py for details! Example usage:
```
> python3 backend_cli.py adjust_currency_tier "Chromatic Orb" -2
```
will modify the tier of Chromatic Orbs by -2.

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

The Python backend communicates return values to AHK by writing them to the file `backed_cli.output`.

**Currently Supported Functions:**
 - `adjust_currency_tier <currency_name> <tier_delta: int> -> None`  (-> indicates return value) 

**Functions To Implement**
 - ...
