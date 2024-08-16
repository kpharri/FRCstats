# This code collects scores (ccwm, opr, and dpr) for all teams in an event. Scores are collected from each team's
# most recent completed event. The scores are collected for every qualifying match that we are taking part in, 
# and the scores are separated according to whether the teams are on our alliance or the opposing alliance. There
# are therefore six sets of scores for each match that we are taking part in.

import requests
import json
import numpy as np
import csv
from datetime import datetime
import operator

team = 'frc4550'
event = '2024mose'
score_type = 'all' # Options are 'opr', 'dpr', 'ccwm', and 'all'

def scored_event(eventkey):
# Determines if the event given by eventkey has performance data available for it on the TBA API.
# The litmus test for this is CCWM data: if the TBA record for the event contains the 'ccwms' field,
# it's assumed the event contains all the other relevant data too.

    tba_event_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+eventkey+'/oprs', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_event = tba_event_json.json()
    if 'ccwms' in tba_event:
        return 1
    return 0

def team_in_event(team,event):
# Checks if a particular team competed in a particular event.
    
    #/event/{event_key}/teams
    tba_event_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+event+'/teams', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_event = tba_event_json.json()
    nteams = len(tba_event)    
    # See if the requested team is in the list:
    for i in range(nteams):
        if tba_event[i]['key'] == team:
            return 1
    return 0

def get_score(team,event,score_type):
# Retrieve a score for a given team's performance in a given event. Function returns a value
# of -1000 if the event does not contain scores, or if the team is not present in the scores list.

    #/event/{event_key}/oprs
    tba_scores_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+event+'/oprs', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_scores = tba_scores_json.json()    
    # Check that scores are available: 
    if 'oprs' in tba_scores:
        # Check that the required team appears in the list of scores:
        if team in tba_scores['oprs']:
            if score_type != 'all':
                return tba_scores[score_type+'s'][team]
            else:
                return [tba_scores['ccwms'][team],tba_scores['oprs'][team],tba_scores['dprs'][team]]
    return -1000

#========== end of function definitions

# Grab the starting date of the current event:
# /event/{event_key}/simple
tba_date_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+event+'/simple', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
tba_date = tba_date_json.json()
event_date = tba_date['start_date']
# Convert the string to python date format:
event_date = datetime.strptime(event_date, "%Y-%m-%d")
print("Starting date of current event: "+str(event_date))

# Get a list of info for all the matches for the current event:
# /team/{team_key}/event/{event_key}/matches/simple
tba_data_json = requests.get('https://www.thebluealliance.com/api/v3/team/'+team+'/event/'+event+'/matches/simple', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
tba_data = tba_data_json.json()
nmatches = len(tba_data)

# Make a data structure to hold a list of all the teams playing in our alliances:
all_teams = [] # 1d list, without duplicates, of all the teams that are taking part in the event.
alliance_scores = [] # list of dictionaries of event scores for our two partners in each match's alliance.
opp_scores = [] # list of dictionaries of event scores for the three opposition teams in each match.
print("Determining our alliance and opposition teams for this event...")
# Cycle through all the qualification matches in this event in order to extract the names of each of our alliances'
# other two teams, and the names of the three opposition teams:
q=0
for i in range(nmatches):
    if tba_data[i]['comp_level'] == 'qm': # Only collect qualifying matches
        q += 1 # Keep a tally of how many quals there are.
        # Look at both the red and blue alliances:
        for k in range(2):
            color = 'blue'
            if k == 1:
                color = 'red'
            # Extract the three teams in the current alliance:
            alliance_list = tba_data[i]['alliances'][color]['team_keys']
            # If we're not in this alliance, it's our opposition alliance, so collect all three names:
            if not team in alliance_list:
                triplet = {'match': tba_data[i]['match_number']}
                for j in range(3):
                    triplet[alliance_list[j]] = 0.0 # Set score to zero for now.
                opp_scores.append(triplet)
            # else this is our alliance, so record our two alliance partners (and not ourselves!):
            else:
                pair = {'match': tba_data[i]['match_number']}
                for j in range(3):
                    if alliance_list[j] != team:                
                        pair[alliance_list[j]] = 0.0 # Set the score equal to zero for now - we'll look it up later
                alliance_scores.append(pair) # Add the team-score pair dictionary to the match list.
# update nmatches to exclude any non-qualifying matches:
nmatches = q

# Now generate a simple 1d list of all teams at the event, which we can use to extract their most recent event
# scores:
#/event/{event_key}/teams
tba_teams_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+event+'/teams', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
tba_teams = tba_teams_json.json()
nteams = len(tba_teams)
for i in range(nteams):
    all_teams.append(tba_teams[i]['key'])

# Now determine each team's most recent scores.
print("Extracting recent "+score_type+" scores for each team in the event...")

temp_scores = {}
if score_type == 'all':
    empty_score = [0.0,0.0,0.0]
else:
    empty_score = 0.0

for p in range(nteams):
    print('...'+all_teams[p])
    # Find the most recent event that the current alliance member took part in (not including the current event)
    # -- Start by getting a list of all the events the member has ever taken part in:
    tba_data_json = requests.get('https://www.thebluealliance.com/api/v3/team/'+all_teams[p]+'/events', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_data = tba_data_json.json()
    # -- Now find the most recent event in the list. Events are mostly chronological, but events occurring within a 
    # single season are not generally in chronological order, so we need to look at just the last few events in the
    # list and find the most recent one.
    nevents = len(tba_data)
    nlast = 6 # Order the last few events in the event list...
    if nevents < nlast:
        nlast = nevents # Unless the team has fewer events in their history than 4, in which case sort all the events
    date_list = []
    for i in range(nevents-nlast,nevents):   
        # Extract the starting date and event key. Save the time as a python date variable:
        test_date = datetime.strptime(tba_data[i]['start_date'],"%Y-%m-%d")
        # Only add the date to the list if it is prior to the current event's date:
        if test_date < event_date:
            date_list.append([tba_data[i]['key'],test_date])
    # Sort the date_list by date:
    date_list = sorted(date_list, key=lambda x: x[1])
    if len(date_list) > 0:
        # Find the most recent valid event in the list. A valid event is one that the team actually took part in,
        # and which has available scores.
        j = len(date_list)-1
        while (get_score(all_teams[p],date_list[j][0],score_type) == -1000) and (j>=0):
            j -= 1
        if j >= 0:
            recent_event = date_list[j][0]
            # Record the team name and their score for this event:    
            temp_scores[all_teams[p]] = get_score(all_teams[p],recent_event,score_type)
        else:
            # No valid recent events for the team, so the team may be a rookie team. Use a score of zero.
            print("   no prior scored events available for team "+all_teams[p])
            temp_scores[all_teams[p]] = empty_score
    else:
        print("   no prior events at all available for team "+all_teams[p])
        temp_scores[all_teams[p]] = empty_score

# Now that we've collected scores, assign them to the teams in our list of alliance scores for each match
# and opposition scores for each match:
for i in range(nmatches):
    for teamname in alliance_scores[i]:
        if teamname != 'match':
            alliance_scores[i][teamname] = temp_scores[teamname]
    for teamname in opp_scores[i]:
        if teamname != 'match':
            opp_scores[i][teamname] = temp_scores[teamname]

# Sort the lists by match number:
alliance_scores = sorted(alliance_scores, key=lambda x: x['match'])
opp_scores = sorted(opp_scores, key=lambda x: x['match'])

print("Writing stats to file...")
# name of csv file   
filename = "team_alliance_scores.csv"
      
# write data to file:
data_file = open("team_alliance_scores.csv", "w")

# Event name:
data_file.write('event,' + event + '\n')
                
# Our team's data:
row = team + ','
if score_type == 'all':
    for i in range(3):
        row += str(temp_scores[team][i]) + ','
else:
    row += str(temp_scores[team])
row += '\n'
data_file.write(row)

# Column titles:
row = 'match,partner1,'
if score_type == 'all':
    score_str = 'ccwm,opr,dpr,'
else: score_str = score_type
row += score_str + 'partner2,' + score_str + 'opp1,' + score_str + 'opp2,' + score_str + 'opp3,' + score_str + '\n'
data_file.write(row)

# Other teams' data:
for i in range(nmatches):   
    # Construct a string containing the current match's info:
    row = str(alliance_scores[i]['match']) + ','
    for teamname in alliance_scores[i]:
        if teamname != 'match':
            row += teamname + ','
            if score_type == 'all':
                for j in range(3):
                    row += str(alliance_scores[i][teamname][j]) + ','
            else:
                row += str(alliance_scores[i][teamname]) + ','
    for teamname in opp_scores[i]:
        if teamname != 'match':
            row += teamname + ','
            if score_type == 'all':
                for j in range(3):
                    row += str(opp_scores[i][teamname][j]) + ','
            else:
                row += str(opp_scores[i][teamname]) + ','
    data_file.write(row+'\n') 
data_file.close()

print("All done")