# PoE Dynamic Loot Filter

![DLF_UI_05_13_2022](https://user-images.githubusercontent.com/37650759/168293570-861da003-836d-4012-a0b2-09da2c8b037f.png)

## What is PoE Dynamic Loot Filter?

**PoE Dynamic Loot Filter** (or **DLF**) is a tool to modify your loot filter seamlessly in real-time while playing Path of Exile.

## Quick Setup

There are only two requirements for DLF to run (see [below](https://github.com/Apollys/PoEDynamicLootFilter#what-setup-is-required) for more details):

1. **[Autohotkey](https://www.autohotkey.com/)**
2. **[Python 3](https://www.python.org/downloads/windows/)**

Once you have the requirements, follow these steps to setup DLF:

1. Download any [FilterBlade](https://www.filterblade.xyz/) loot filter (you can leave it in your Downloads directory).
2. Download this repository anywhere on your PC.
3. Open this PoEDynamicLootFilter directory in command prompt, and run `python setup.py`.

Once this is complete, double click `dynamic_loot_filter.ahk` to launch PoE DLF.

## In-Game Usage

1. While playing Path of Exile, press a hotkey (default: `F8`) to open the UI.
2. Select your changes with just a couple mouse clicks.
3. Click **Apply Changes** - the GUI will automatically close and your loot filter will automatically be updated.
4. In-game, press `o` (options) and click the **Reload Filter** button - your changes are now visible immediately in-game!

## Why Use DLF?

Normally, in order to make a change to our filter, we need to:
1. Alt-tab out of PoE
2. Navigate to the Filterblade site and log in if not logged in
3. Load our Filterblade filter
4. Search through the Filterblade UI to find the section corresponding to the change we want to make
5. Make the change
6. Save the filter on Filterblade
7. Sync the changes to our Path of Exile account
8. Alt-tab back into PoE
9. Reload the filter

With DLF, this can all be done in a couple seconds. No exaggeration here.

Common highly valuable uses include:

1. I'm getting to mapping and no longer want to see single portal and wisdom scrolls.  With PoE DLF,
   I can easily set the minimum visible stack size of currency by tier (portal and wisdom scrolls have their own tier).
2. I'm farming chaos recipes, and have way too many body armors, but not enough hats.  With PoE DLF,
   I can easily show/hide chaos recipe rare items by item slot.
3. My loot filter is getting spammed by something random.  DLF may have a specific option to fix it
   (for example, if it's a cheap div card, I could raise the minimum shown div card tier threshold), or 
   I can use DLF's built-in rule-matcher to automatically detect and hide the rule that matches a given item.
   
## DLF Requirements

PoE DLF has minimal requirements and setup to make it as widely accessible as possible.  You need the following:
 * A **loot filter created from [Filterblade](https://www.filterblade.xyz/)** - using a builtin filter (e.g. Neversink Stable - Strict) is totally fine!
   In fact, the less you've moved things around or created custom rules in FilterBlade, the better (visual style changes are always okay though)
 * **[Autohotkey](https://www.autohotkey.com/)** - if you're playing PoE and don't have this already, you really should
 * **[Python 3](https://www.python.org/downloads/windows/)** - the version is important here, it needs to be **Python 3**
   * To verify your python is set up as required, open a command prompt and type `python`: it should launch Python 3.X)
   * No specific python packages are required, as long as Python 3 loads, you are good to go
 * **DLF config**: in your profile config file, tell DLF the path to your downloaded filter and the path to Path of Exile

## Under the Hood - How Does DLF Work?

Firstly, since we are programmatically reading, analyzing, and writing filter files, note that this is all done *locally*
 - on the user's machine - rather than online.

Filterblade formats its loot filters in a certain way, and PoE DLF leverages that format to parse the input filter into
a structure that it can understand and manipulate.  For example, Filterblade places `type` and `tier` tags on the first
line of their rules, so the tier 1 currency rule can be found by looking for the tags `type->currency` and `tier->t1`.

Whenever the user wants to make a change to the filter, the corresponding rules are modified, and the filter is re-saved.
User profiles are also updated to save the changes the user has made to the filter, so the user can re-download a filter
(if they want to make a change on the Neversink site), and all their DLF changes will be maintained.  Users can also maintain
separate profiles (e.g. for different characters, for SSF/Trade leagues, etc) if desired.

All filter parsing, modification, and saving is done by a Python backend.  An AHK frontend GUI presents the program's functionality
in a clean and efficient manner to the user, and the AHK GUI then relays commands to the Python backend to execute.

Rule matching is a somewhat complicated - the python backend has to reproduce Path of Exile's entire rule-item matching algorithm.
In general, it works pretty well, but note that some aspects of it have been shortcut slightly, as they're not super important
and the system takes a lot of work to get perfectly.  Also, note that at new league starts, there may be significant bugs
because of new items and loot filter attributes that are added to the game.

- - -

**End of user Readme: non-developers may safely ignore everything below.**

- - -

## Developer Documentation

### Syntax for backend command-line interface calls

```
> python backend_cli.py <function_name> <function_parameters...> <profile_name (if required)>
```

The `profile_name` parameter is required in all cases except for:
 - `get_all_profile_names`
 - `set_active_profile`

- - -

### To-Do

Feature suggestions and bug reports are now tracked in GitHub issues.
I will just leave items that do not have a corresponding GitHub issue here for now.

 - [ ] Skip unrecognized commands in Profile.changes file (with warning)
   - Likely cause is depracated feature from version update
   - Better not to fail in this case
 - [ ] Refactor frontend AHK script
   - [x] Reorder and organize build GUI code
   - [ ] Write helper functions to make GUI construction more concise.
         For example, combining setting font with creating an item
   - [x] Resolve minor questions in AHK script (ctr-f TODO)
   - [ ] Refactor all of the code to be more modular

- - -

### Frontend-Backend API Specification

The AHK frontend calls the Python backend via:
```
> python backend_cli.py <function_name> <function_parameters...> <profile_name (if required)>
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
  - `check_filters_exist`
  - `import_downloaded_filter`
  - `reload_input_filter`
  - `run_batch`
  - `get_rule_matching_item`
  - `set_rule_visibility <type_tag: str> <tier_tag: str> <visibility: {show, hide, disable}>`
  - `set_currency_to_tier <currency_name: str> <tier: int>`
  - `get_all_currency_tiers`
  - `set_currency_tier_min_visible_stack_size <tier: int> <visible_flag: int>`
  - `get_currency_tier_min_visible_stack_size <tier: int>`
  - (For test suite use: `get_tier_of_currency <currency_name: str>`)
  - `get_all_essence_tier_visibilities`
  - `set_hide_essences_above_tier <tier: int>`
  - `get_hide_essences_above_tier`
  - `get_all_div_card_tier_visibilities`
  - `set_hide_div_cards_above_tier <tier: int>`
  - `get_hide_div_cards_above_tier`
  - `get_all_unique_item_tier_visibilities`
  - `set_hide_unique_items_above_tier <tier: int>`
  - `get_hide_unique_items_above_tier`
  - `get_all_unique_map_tier_visibilities`
  - `set_hide_unique_maps_above_tier <tier: int>`
  - `get_hide_unique_maps_above_tier`
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
