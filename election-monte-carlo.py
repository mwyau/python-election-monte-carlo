import csv
import pickle
import us
import numpy as np
from scipy.stats import norm
try:
    from numpy import random_intel as random # Use Intel random if available
except ImportError:
    from numpy import random

from pollster import Pollster

# Get state names from us.STATES
states = {state.abbr:state.name for state in us.STATES}

# Read electoral college votes from csv file
# https://raw.githubusercontent.com/chris-taylor/USElection/master/data/electoral-college-votes.csv
with open('electoral-college-votes.csv') as csvfile:
    reader = csv.reader(csvfile)
    college = {row[0]:int(row[1]) for row in reader}

# Initialize Pollster API
pollster = Pollster()

date = '2016-11-01' # 1 weeks of polls between 2016-11-01 and 2016-11-07
polls = []
page = 1

query = pollster.polls(topic='2016-president', after=date, page=page)
while query:
    polls.extend(query)
    query = pollster.polls(topic='2016-president', after=date, page=page)
    page +=1

# Save polls by pickle
pickle.dump(polls, open('polls.p', 'wb'))

# Keep only state polls, igore national polls
state_questions = [question for poll in polls for question in poll.questions 
                if question['topic'] == '2016-president' and question['code'].split('-')[1] in states]

# Correct for the state labels
for question in state_questions:
    if question['state'] == 'US':
        question['state'] = question['code'].split('-')[1]

# Number of valid polls by state
polls_by_state_counts = {state : sum(question['state'] == state for question in state_questions)
                     for state in states}

# Each state is a dictionary of arrays
# obs: poll size
# dem: Democrat popular vote percentage
# rep: Republican popular vote percentage
polls_by_state = {state: {'obs':[], 'dem':[], 'rep':[]} for state in states}
for question in state_questions:
    state = question['state']
    obs = question['subpopulations'][0]['observations']
    dem = ''
    rep = ''
    for response in question['subpopulations'][0]['responses']:
        if response['last_name'] == 'Clinton':
            dem = response['value']
        if response['last_name'] == 'Trump':
            rep = response['value']
    # Check for empty responses
    if state and obs and dem and rep:
        polls_by_state[state]['obs'].append(obs)
        polls_by_state[state]['dem'].append(dem)
        polls_by_state[state]['rep'].append(rep)

state_mean_dem = {}
state_std_dem = {}
state_cdf_dem = {}

for state, poll in polls_by_state.items():
    dem = np.array(poll['dem'])
    rep = np.array(poll['rep'])
    obs = np.array(poll['obs'])
    dem_mean = np.average(dem, weights=obs)
    rep_mean = np.average(rep, weights=obs)
    state_mean_dem[state] = dem_mean/(dem_mean+rep_mean)*100
    
    state_std_dem[state] = np.sqrt(np.average(np.square(dem-dem_mean)+
                                              (100-dem)*dem/10000, weights=obs))/(dem_mean+rep_mean)*100
        
    state_cdf_dem[state] = norm.cdf((state_mean_dem[state]-50)/state_std_dem[state])

# Number of Monte Carlo simulations
n_run = 100000
random_numbers = random.rand(n_run,len(states))

college_total = sum(college.values()) # Total electoral college votes
college_required = college_total/2 # Electoral college votes required to win
college_dem = np.zeros(n_run) # Democrats' total electoral college votes

# Magic
for i, r in enumerate(random_numbers):
    for state_index, state in enumerate(state_cdf_dem):
        if r[state_index] < state_cdf_dem[state]:
            college_dem[i] += college[states[state]]

# Hillary's chance to win
chance = sum(college_dem > college_required)/n_run*100
print('Hillary Clinton has a {0:.3f}% chance to win.'.format(chance))
print('Median of Hillary Clinton\'s electoral votes: {}'.format(int(np.median(college_dem))))
print('Median of Donald Trump\'s electoral votes: {}'.format(int(college_total-np.median(college_dem))))
