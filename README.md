What does matchscores_v2.py do?
===============================
This code retrieves, from the Blue Alliance API, scores (ccwm, opr, and dpr) for all FRC teams that are taking part in a desired event. Scores are collected from each team's most recent fully completed event. The scores are collected for every qualifying match in the current event that your team is taking part in, and the scores are separated according to whether the teams are on your alliance or on the opposing alliance. There are therefore six sets of scores for each match that you are taking part in.

The purpose is to get a rough idea of how well your team, and its alliances, stack up against the competition. The code is intended to be run during a competition - it does not depend on statistics created during that competition, only during all the teams' most recent completed competition, which may be another event from the same season, or their last event from the previous season.

Because Wi-Fi is difficult to find at events, the code is meant to be run once when Wi-Fi is available, perhaps at a hotel the night before, for example. The code produces a .CSV file whose contents are pasted into an Excel spreadsheet that plots the data to make interpretation more user-friendly. That spreadsheet can then be studied at the event without depending on Wi-Fi.

In this repository are:
- matchscores_v2.py. This is the main code. The 'requests' and 'numpy' libraries will have to be installed in order for the code to run. To set up the code for your team and your current event, modify the 'team' and 'event' variables near the top of the code. These need to be in the format used by the Blue Alliance API, for example 'frc4550' for team 4550, and '2024mose' as the code for the 2024 Missouri regional.
- team_alliance_scores.csv. This is an example of the output produced by the code.
- frc4550_missouri_v2.xlsx. This is the Excel spreadsheet that crunches the data in the above .CSV file, and plots useful graphs. Simply download this and paste your own .CSV data into the first Sheet on the spreadsheet, and the graphs will automatically update to show your data.

What does matchscores_v2.py do?
