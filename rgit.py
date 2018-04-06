#!/usr/bin/env python3

import argparse
import configparser
import sys

import rgit-data as rdata
import rgit-utils as rutils

config_path = "~/.config/rgit.ini"
config_defaults = {
    "TrackDotfiles": "False",
    "GitRoot": "~/git",
    "GitDepth": "24",
    "Path": "~/.rgit"
}

def requireConfigOpts(config):
    if not config.has_option("device", "id"):
        raise Exception("No device id specified in config")

    if not config.has_option("data", "remote"):
        raise Exception("No remote specified in config")

    if (config.getboolean("rgit", "trackDotfiles", False)
                        and (not config.has_option("rgit", "dotfilesGitCmd"))):
        raise Exception("TrackDotfiles is true"
                        " but DotfilesGitCmd is not specified in config")


def rgitRawAction(arg):
    curr_repo_path = os.path.join(config["data"]["path"],
                                  "data", rutils.getRepoId)
    all_files = os.listdir(curr_repo_path)
    dirs = list(filter(lambda x: os.isdir(x), ))

    for device in dirs:
        path = os.path.join(curr_repo_path, device, arg)

        if not os.exists(path):
            continue

        print("[rgit] device: {0}".format(device))
        if os.isfile(path):
            with open(path, 'r') as fin:
                print (fin.read())
        elif os.isdir(path):
            print("[rgit] Listing <{0}> directory!".format(arg))
            indent="    "
            for filename in os.listdir(path):
                print(indent + filename)
            print(filename)
        else:
            raise Exception("<{0}> is neither regular file or directory - wtf?"
                            .format(path))

    if len(dirs) == 0:
        print("[rgit] Could not find <{0}> for any device!".format(device))


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

    config = configparser.ConfigParser(config_defaults)
    config.read(config_path)

    if args.action == "help" or args.help:
        parser.print_help()
        sys.exit 0
    
    if args.action == "raw":
        if args.action_arg == "":
            raise Exception("No path provided for 'raw' action.")
        rgitRawAction(args.action_arg)
        sys.exit 0

    if args.action == "data":
        if args.action_arg == "":
            raise Exception("No argument provided for 'data' action.")
        rgitDataAction(args.action_arg)
        sys.exit 0


if __name__ == "__main__":
    main()
