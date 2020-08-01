# pydfs-lineup-optimizer Repository Change Log

All notable changes to this project will be documented in this file.

## [v3.3.0]
- Added ability to print statistic after optimization run
- Added cyclic spacing handling for set_spacing_for_positions method 
- Added ability to change algorithm for exposure calculation
- Added min games rule for DK optimizers
- Added DK CSGO
- Added DK Tiers
- Added nascar/mma for FD
- Refactored export
- Refactored FanDuel single game optimizers
- Fixed Yahoo export
- Fixed restrict from opposing team method with max_allowed parameter

## [v3.2.0]
- Added randomize with projections range
- Added max allowed parameter for restrict positions from opposing team
- Fixed team stacking with spacing
- Fixed ignore max_exposure in groups
- Fixed FD Golf
- Fixed yahoo import
- Fixed FD NFL positions names

## [v3.1.1]
- Fixed position names and ordering for FanDuel LOL classic

## [v3.1.0]
- Added LOL for FanDuel
- Fixed FanDuel Single Game incorrect lineups

## [v3.0.1]
- Fixed paring teams in DK

## [v3.0.0]
- Added new stacking api
- Fixed min exposure
- Added FanDuel NBA Single Game
- Added sorting of players in lineup by game start time
- Added export lineups for Fantasy Draft
- Added confirmed starters rule
- Fixed total teams rule for DK NHL
- Fixed NHL export for DK
- Dropped python 2 support
- Added python 3.8 support

## [v2.7.0]
- Added rule for restricting players from same team
- Added ability to specify several positions in stack
- Added FanDuel Golf
- Added ability to set player specific deviation for randomness mode
- Added rule for forcing players from opposing team
- Added ability to change default timezone
- Added set total teams rule
- Improved performance of positions for same team rule
- Removed dropping of lowest score in FD NBA
- Added missed DK Hockey min teams rule
- Added average ownership to lineup printing
- Fixed Yahoo Hockey settings positions

## [v2.6.2]
- Fixed python 2.7 support

## [v2.6.1]
- Added soccer for DK Captain Mode
- Added Fanduel minimum teams restriction
- Fixed export for DK

## [v2.6.0]
- Added ability to specify multiple positions stacks in positions for same team rule
- Added teams exposure rule
- Added ability to create stacks for specific positions
- Added parsing of min exposure and projected ownership from csv
- Improved performance for positions rule for multi-positional sports
- Improved performance for max repeating players rule
- Decreased number of created solver constraints for exposures rules

## [v2.5.1]
- Fixed optimization for roster spacing rule
- Fixed repeated lineups issue when optimizing in random mode

## [v2.5.0]
- Added lineup ordering rule
- Added DK NASCAR
- Added DK Tennis
- Added DK WNBA
- Added DK Captain Mode WNBA
- Added search by player id
- Added game info parsing for captain mode
- Fixed bug with total player for late-swap
- Fixed generating lineups with CPLEX solver
- Fixed game info parsing for individual sports
- Fixed minimum hitters FD rule
- Improved performance for sports without multi-positional players

## [v2.4.1]
- Fixed solver freezes on windows

## [v2.4.0]
- Added DK MLB captain mode
- Added teams stacking
- Added constraint for restricting players from opposing teams
- Fixed bug with duplicated positions in DK MLB late-swap
- Fixed default timezone for DK late-swap
- Improved performance for solver setup
- Added ability to change solver in PuLP

## [v2.3.0]
- Added DK late-swap
- Added DK MMA
- Fixed DK LOL settings
- Fixed FantasyDraft Golf settings
- Fixed DK captain mode settings

## [v2.2.1]
- Fixed import error for optimizer running on python 3.6

## [v2.2.0]
- Added DK captain mode
- Added minimum exposure
- Improved normal objective optimization
- Added DK template file format
- Fixed DK LOL settings

## [v2.1.0]
- Added projected ownership feature
- Added FanBall football
- Fixed FanDuel MLB max player from one team constraint

## [v2.0.3]
- Fixed FanDuel nfl settings

## [v2.0.2]
- Fixed FanDuel mlb settings

## [v2.0.0]
- Added custom constraints creation
- Optimized lineup generation speed
- Added max repeating players constraint
- Added new sports

## [v1.4.1]
- Changed settings for DraftKings

## [v1.4]
- Added min salary constraint.

## [v1.3]
- Fixed bug with setting lineup positions

## [v1.2]
- Added csv export
- Added constraints for positions in same team
- Changed constraint setting interface

