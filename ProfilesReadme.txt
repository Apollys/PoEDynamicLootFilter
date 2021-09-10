Profiles

Each profile is defined by a required .config and optional .rules and .changes files:
 - The .config file specifies all configurable settings for the profile.
 - The .rules file lists additional rules to be added to the *start* of the downloaded filter.
 - The .changes file tracks all changes made to the filter, which are re-applied on re-import.
 
In addition, there is a single general config file in which the user
specifies the currently active profile: "general.config".
 
All profile files must be located directly inside the directory "Profiles".

For example, if you want to have a profile called "Leaguestart" and a profile called
"Endgame", your Profiles directory should contain the following files:
 - general.config
 - Leaguestart.config
 - [optional] Leaguestart.rules
 - [optional] Leaguestart.changes
 - Endgame.config
 - [optional] Endgame.rules
 - [optional] Endgame.changes

Note: the .config file should follow the format of the given DefaultProfile.config.
