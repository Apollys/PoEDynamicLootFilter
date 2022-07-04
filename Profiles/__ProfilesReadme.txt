Profiles

Note: these files are generated automatically via Profile creation workflow, so you should
not have to deal with them unless you want to add custom rules to the .rules file, or debug
some weird issue.

Each profile is defined by a required .config and optional .rules and .changes files:
 - The .config file specifies all configurable settings for the profile.
 - The .rules file lists additional rules to be added to the *start* of the downloaded filter.
 - The .changes file tracks all changes made to the filter, which are re-applied on filter import.
 
In addition, there is a single general config file, "config/general.config", which contains
the currently active profile and the UI hotkeys.
 
All profile files must be located directly inside the directory "Profiles".

For example, if you want to have a profile called "Leaguestart" and a profile called
"Endgame", your Profiles directory should contain the following files:
 - Leaguestart.config
 - [optional] Leaguestart.rules
 - [optional] Leaguestart.changes
 - Endgame.config
 - [optional] Endgame.rules
 - [optional] Endgame.changes
