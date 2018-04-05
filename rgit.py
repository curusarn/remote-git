#!/usr/bin/env python3

import argparse
import configparser
import sys

import rgit-data
import rgit-utils

config_path = "~/.config/rgit.ini"

def rgitRaw():
    curr_repo_path = os.path.join(config["data"]["path"], "data", getRepoId)
    # get files 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dotfiles', action="store_true",
                        default=False, help="Assume dotfiles")
    parser.add_argument('-h', '--help', action="store_true", default=False, 
                        help="Display this help")
    possible_actions = ("help", "data", "raw")
    parser.add_argument('action', action="store", choices=possible_actions,
                        help="Action to perform")
    parser.add_argument('action_arg', action="store", nargs="?", default="",
                        help="Action argument")
    args = parser.parse_args

    config = configparser.ConfigParser()
    config.read(config_path)

    if args.action == "help" or args.help:
        parser.print_help()
        sys.exit 0
    
    if args.action == "raw":
        if args.action_arg == "":
            raise Exception("No path provided for 'raw' action.")
        rgitRaw()
        sys.exit 0

    if args.action == "data":
        if args.action_arg == "":
            raise Exception("No argument provided for 'data' action.")
        sys.exit 0


if __name__ == "__main__":
    main()
