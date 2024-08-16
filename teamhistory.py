# To do: 
# - print the actual date of the comp so that the events can be organized chronologically at the level
# of months rather than years.
# - start looking at how the qual match schedule influences ranking

import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import csv

plt.rcParams["figure.figsize"] = [7.0, 5.0]
plt.rcParams["figure.autolayout"] = True
team = 'frc4550'
# Get a list of all events for the team:
tba_data_json = requests.get('https://www.thebluealliance.com/api/v3/team/'+team+'/events', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
tba_data = tba_data_json.json()

# Weed out events that contain no useful data by looking for ccwm values. If no values are present,
# the event is considered to have no useful data:
i = 0
badentry = 0
while i < len(tba_data):
    tba_event_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+tba_data[i]['key']+'/oprs', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_event = tba_event_json.json()
    if 'ccwms' in tba_event:
        i += 1
    else:
        del tba_data[i]

ncomps = len(tba_data)
print('Analysing '+str(ncomps)+' events...')

# stats will have a row for every comp. Each row contains year, city, event key, average score, ccwm, opr, dpr, and rank.
stats = np.zeros(ncomps, dtype={'names':('year', 'city', 'key', 'avgscore', 'ccwm', 'opr', 'dpr', 'rank'),
                          'formats':('U4', 'U15', 'U9', 'f', 'f', 'f', 'f', 'i4')})

for i in range(ncomps):
    print("Generating data for comp "+str(i+1)+" of "+str(ncomps)+"...")
    
    # Record event info:
    stats[i]['year'] = tba_data[i]['year']
    stats[i]['city'] = tba_data[i]['city']
    stats[i]['key'] = tba_data[i]['key']

    # Retrieve match scores, in order to compute average score for the comp, for normalization purposes:
    tba_match_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+tba_data[i]['key']+'/matches', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_match = tba_match_json.json()
    nmatch = len(tba_match)
    avgscore = 0.0
    for j in range(nmatch):
        avgscore += tba_match[j]['alliances']['blue']['score']
        avgscore += tba_match[j]['alliances']['red']['score']
    if nmatch > 0:
        avgscore = avgscore/(2.0*float(nmatch))
    stats[i]['avgscore'] = avgscore

    # Retrieve opr, dpr, and ccwm:
    tba_event_json = requests.get('https://www.thebluealliance.com/api/v3/event/'+tba_data[i]['key']+'/oprs', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_event = tba_event_json.json()
    if 'ccwms' in tba_event:
        stats[i]['ccwm'] = tba_event['ccwms'][team]
    else:
        stats[i]['ccwm'] = 0.0
    if 'oprs' in tba_event:
        stats[i]['opr'] = tba_event['oprs'][team]
    else:
        stats[i]['opr'] = 0.0
    if 'dprs' in tba_event:
        stats[i]['dpr'] = tba_event['dprs'][team]
    else:
        stats[i]['dpr'] = 0.0

    # Retrieve team ranking for the event:
    tba_event_json = requests.get('https://www.thebluealliance.com/api/v3/team/'+team+'/event/'+tba_data[i]['key']+'/status', headers={"X-TBA-Auth-Key": "8grDWPIjybaddgFdJiR69XjFj9Re6QzApVOhhesbb8aI7PF6itoLMnuzZegCgZYz"})
    tba_event = tba_event_json.json()
    if 'qual' in tba_event:
        if type(tba_event['qual']).__name__ != 'NoneType':
            stats[i]['rank'] = tba_event['qual']['ranking']['rank']
    else:
        stats[i]['rank'] = 0

print("Writing stats to file...")
# name of csv file   
filename = "team4550stats.csv"
      
# writing to csv file   
with open(filename, 'w', newline='') as csvfile:   
    # creating a csv writer object   
    csvwriter = csv.writer(csvfile)   
                     
    # write the data rows   
    csvwriter.writerows(stats) 

print("All done")
