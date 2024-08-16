# This code collects scores (ccwm, opr, and dpr) for all teams that will, at some point, be in an alliance with us
# during a given event. Scores are taken from those teams' most recent events (i.e., not the current event).
#
# See v2 of the code if you want to retrieve scores for all six teams in each match, in order to compare our
# alliance with the opposition alliance.

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
# Checks is a particular team competed in a particular event.
    
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
alliance_teams = [] # 1d list, without duplicates, of all the teams that will appear in our alliances
                    # at some point during the event.
alliance_scores = [] # list of dictionaries for event scores for our two partners in each match's alliance.
print("Determining our alliance teams for this event...")
# Cycle through all the qualification matches in this event in order to extract the names of each of our alliances'
# other two teams:
q=0
for i in range(nmatches):
    if tba_data[i]['comp_level'] == 'qm': # Only collect qualifying matches
        q += 1 # Keep a tally of how many quals there are.
        # Extract the three teams in the blue alliance:
        alliance_list = tba_data[i]['alliances']['blue']['team_keys']
        # If our team is not in this alliance, then extract the red alliance instead:
        if not team in alliance_list:
            alliance_list = tba_data[i]['alliances']['red']['team_keys']
        # Record our two alliance partners (and not ourselves!):
        pair = {'match': tba_data[i]['match_number']}
        for j in range(3):
            if alliance_list[j] != team:
                alliance_teams.append(alliance_list[j])
                pair[alliance_list[j]] = 0.0 # Set the score equal to zero for now - we'll look it up later
        alliance_scores.append(pair) # Add the team-score pair dictionary to the match list.
# update nmatches to exclude any non-qualifying matches:
nmatches = q
# Remove duplicates:
alliance_teams = list(dict.fromkeys(alliance_teams))
# Add ourselves, because we also have to find our own score from our own most recent event:
alliance_teams.append(team)
nallies = len(alliance_teams)

# Now that we have a list of our alliance partners for this event, determine each partner's most recent score.
print("Extracting recent "+score_type+" score for each alliance member...")

temp_scores = {}
if score_type == 'all':
    empty_score = [0.0,0.0,0.0]
else:
    empty_score = 0.0

for p in range(nallies):
    print('...'+alliance_teams[p])
    # Find the most recent event that the current alliance member took part in (not including the current event)
    # -- Start by getting a list of all the events the member has ever taken part in:
    tba_data_json = requests.get('https://www.thebluealliance.com/api/v3/team/'+alliance_teams[p]+'/events', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
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
        #while ((scored_event(date_list[j][0]) == 0) or (team_in_event(alliance_teams[p],date_list[j][0]) == 0)) and (j>=0):
        #    j -= 1
        while (get_score(alliance_teams[p],date_list[j][0],score_type) == -1000) and (j>=0):
            j -= 1
        if j >= 0:
            recent_event = date_list[j][0]
            # Record the alliance name and their score for this event:    
            temp_scores[alliance_teams[p]] = get_score(alliance_teams[p],recent_event,score_type)
        else:
            # No valid recent events for the team, so the team may be a rookie team. Use a score of zero.
            print("   no prior scored events available for team "+alliance_teams[p])
            temp_scores[alliance_teams[p]] = empty_score
    else:
        print("   no prior events at all available for team "+alliance_teams[p])
        temp_scores[alliance_teams[p]] = empty_score

# Now that we've collected scores, assign them to the teams in our list of alliance scores for each match:
for i in range(nmatches):
    for teamname in alliance_scores[i]:
        if teamname != 'match':
            alliance_scores[i][teamname] = temp_scores[teamname]

# Sort the list by match number:
alliance_scores = sorted(alliance_scores, key=lambda x: x['match'])

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
row += score_str + 'partner2,' + score_str + '\n'
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
    data_file.write(row+'\n') 
data_file.close()

print("All done")