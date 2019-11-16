#!/usr/bin/env python3

import argparse
import json
import os
import requests
import sys
import my_data
from my_data import USR
from my_data import KEY


class Debug(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        import pdb; pdb.set_trace()


# MAIN
parser = argparse.ArgumentParser(description="Increases health points if less than given threshold")
parser.add_argument('-p', '--hp', '--healthpoints',
                    type=int, default=30,
                    help='Minimum HP (default=10)')
parser.add_argument('-m', '--multiplier',
                    type=int, default=5,
                    help='Multiplier (default=5)')
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
args.baseurl += "/api/v3/user"

args.user_id = USR
args.api_token = KEY

headers = {"x-api-user": args.user_id, "x-api-key": args.api_token, "Content-Type": "application/json"}

req = requests.get(args.baseurl, headers=headers)

print(args)
