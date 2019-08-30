#!/usr/bin/env python3

import argparse
import os
import requests
import time
import six
import sys
import datetime
import my_data 
from my_data import USR, KEY


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

        #put your user id as the second argument
        args.user_id = USR
except KeyError:
    print("User ID must be set by the -u/--user-id option or by setting the environment variable 'HAB_API_USER'")
    sys.exit(1)

try:
    if args.api_token is None:

        #put your api token as the second argument
        args.api_token = KEY
except KeyError:
    print("API Token must be set by the -k/--api-token option or by setting the environment variable 'HAB_API_TOKEN'")
    sys.exit(1)


headers = {"x-api-user": args.user_id, "x-api-key": args.api_token, "Content-Type": "application/json"}

today = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
today = today + datetime.timedelta(days=1)
today = str(today)
duetoday = []
dueaftertoday = []

req = requests.get(args.baseurl + "tasks/user?type=todos", headers=headers)

for todo in req.json()['data']:
    # To send all overdue todos to the top:     todo['date'][:10] <= today:
    if 'date' in todo and todo['date'] and todo['date'][:10] <= today:
        duetoday.append(todo)
    # To send all the todos due after today to right below the overdue todos:   todo['date'][:10] > today:
    elif 'date' in todo and todo['date'] and todo['date'][:10] > today:
        dueaftertoday.append(todo)

# Put all of the overdue todos at the top with the most overdue at the top
count = 0
for todo in sorted(duetoday, key=lambda k: k['date'], reverse=False):
    requests.post(args.baseurl + "tasks/" + todo['id'] + "/move/to/" + str(count), headers=headers)
    count = count + 1

# Put the todos that are due in the shortest amount of time after today
for todo in sorted(dueaftertoday, key=lambda k: k['date'], reverse=True):
    requests.post(args.baseurl + "tasks/" + todo['id'] + "/move/to/" + str(count), headers=headers)
    
