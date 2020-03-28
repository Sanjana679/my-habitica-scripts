#!/usr/bin/env python3

import argparse
import os
import requests
import time
import six
import sys
import datetime
import my_data
from my_data import USR
from my_data import KEY



class Debug(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        import pdb; pdb.set_trace()

# MAIN
parser = argparse.ArgumentParser(description="Moves active tasks with duedates to the top of the To-Dos list (excluding todos with future due dates)")
parser.add_argument('-u', '--user-id',
                    help='From https://habitica.com/#/options/settings/api\n \
                    default: environment variable HAB_API_USER')
parser.add_argument('-k', '--api-token',
                    help='From https://habitica.com/#/options/settings/api\n \
                    default: environment variable HAB_API_TOKEN')
parser.add_argument('--baseurl',
                    type=str, default="https://habitica.com",
                    help='API server (default: https://habitica.com)')
parser.add_argument('--debug',
                    action=Debug, nargs=0,
                    help=argparse.SUPPRESS)
args = parser.parse_args()
args.baseurl += "/api/v3/"

try:
    if args.user_id is None:
        args.user_id = USR
except KeyError:
    print("User ID must be set by the -u/--user-id option or by setting the environment variable 'HAB_API_USER'")
    sys.exit(1)

try:
    if args.api_token is None:
        args.api_token = KEY
except KeyError:
    print("API Token must be set by the -k/--api-token option or by setting the environment variable 'HAB_API_TOKEN'")
    sys.exit(1)


headers = {"x-api-user": args.user_id, "x-api-key": args.api_token, "Content-Type": "application/json"}

today = time.strftime("%Y-%m-%d", time.localtime())
today = str(today)

duetoday = []
duebeforetoday = []
dueaftertoday = []
notdue = []

dailies = []

req_tags = requests.get(args.baseurl + "tags", headers=headers)
req_todos = requests.get(args.baseurl + "tasks/user?type=todos", headers=headers)
req_dailies = requests.get(args.baseurl + "tasks/user?type=dailys", headers=headers)


'''
Sorting by tag and due date doesn't work too well in practice, but I'm going to leave it be for now
'''

for tag in req_tags.json()['data']:
    for todo in req_todos.json()['data']:
        # To send only today's todos to the top:    todo['date'][:10] == today:
        # To send all overdue todos to the top:     todo['date'][:10] < today:

        #if the todo has a tag
        if(len(todo['tags']) != 0):

            if 'date' in todo and todo['date'] and todo['date'][:10] == today and todo['tags'][0] == tag['id']:
                duetoday.append(todo)
            
            elif 'date' in todo and todo['date'] and todo['date'][:10] > today and todo['tags'][0] == tag['id']:
                dueaftertoday.append(todo)
            
            elif 'date' in todo and todo['date'] and todo['date'][:10] < today and todo['tags'][0] == tag['id']:
                duebeforetoday.append(todo)
            
            elif todo['tags'][0] == tag['id']: 
                notdue.append(todo)

        #if the todo does not have a tag
        else:
            if 'date' in todo and todo['date'] and todo['date'][:10] == today:
                duetoday.append(todo)
            
            elif 'date' in todo and todo['date'] and todo['date'][:10] > today:
                dueaftertoday.append(todo)
            
            elif 'date' in todo and todo['date'] and todo['date'][:10] < today:
                duebeforetoday.append(todo)
            
            else:
                notdue.append(todo)

    for daily in req_dailies.json()['data']:
        
        if daily['tags'][0] == tag['id']:
            dailies.append(daily)
    
            

count = 0
# Push overdue todos to the top
for todo in sorted(duebeforetoday, key=lambda k: k['date'], reverse=False):
    requests.post(args.baseurl + "tasks/" + todo['id'] + "/move/to/" + str(count), headers=headers)
    count = count + 1

# Push today's todos afterwards
for todo in [t for t in duetoday if t['date'][:10] == today]:
    requests.post(args.baseurl + "tasks/" + todo['id'] + "/move/to/" + str(count), headers=headers)
    count = count + 1

# Push todos after today afterwards
for todo in sorted(dueaftertoday, key=lambda k: k['date'], reverse=False):
    requests.post(args.baseurl + "tasks/" + todo['id'] + "/move/to/" + str(count), headers=headers)
    count = count + 1

for todo in notdue:
    requests.post(args.baseurl + "tasks/" + todo['id'] + "/move/to/" + str(count), headers=headers)
    count = count + 1

count = 0
for daily in dailies:
    requests.post(args.baseurl + "tasks/" + daily['id'] + "/move/to/" + str(count), headers=headers)
    count = count + 1
