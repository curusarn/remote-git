#!/usr/bin/env python3

import argparse
import configparser
import os
import sys

import rgit_data as rdata
import rgit_utils as rutils

config_path = os.path.expanduser("~/.config/rgit.ini")
config_defaults = {
    "TrackDotfiles": "False",
    "GitRoot": "~/git",
    "GitDepth": "24",
    "Path": "~/.rgit",
    "DotfilesGitCmd": ""
}

def requireConfigOpts(config, args):
    if not config.has_option("device", "id"):
        raise Exception("No device id specified in config")

    if not config.has_option("data", "remote"):
        raise Exception("No remote specified in config")

    if (config["rgit"]["dotfilesGitCmd"] == ""):
        if (config.getboolean("rgit", "trackDotfiles", False)):
            raise Exception("TrackDotfiles is True"
                            " but DotfilesGitCmd is not specified in config")
        if (args.dotfiles):
            raise Exception("--dotfiles option is present"
                            " but DotfilesGitCmd is not specified in config")


def rgitRawAction(config, arg, dotfiles=False):
    git_cmd = "git"
    if dotfiles: 
        git_cmd = config["rgit"]["dotfilesGitCmd"]
    repo_id = rutils.getRepoId(os.getcwd(), git_cmd)

    curr_repo_path = os.path.join(config["data"]["path"], "data",
                                  repo_id.decode("utf-8"))

    dirs = rutils.listDirFilterOnlyDirectories(curr_repo_path)

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


def rgitDataAction(config, arg, dotfiles=False):
     
    if arg == "session-exit":
        rdata.pull(config["data"]["remote"], config["data"]["path"])

        rdata.initRecordCmds(config["rgit"]["gitDepth"])
        rdata.record(config["rgit"]["gitRoot"], config["data"]["path"],
                     config["device"]["id"], config["rgit"]["dotfilesGitCmd"])
        
        rdata.commit(config["data"]["path"], config["device"]["id"])

        rdata.push(config["data"]["path"])

    elif arg == "session-start":
        rdata.pull(config["data"]["remote"], config["data"]["path"])
     
    elif arg == "clone":
        rdata.clone(config["data"]["remote"], config["data"]["path"])

    elif arg == "setup":
        if not rutils.isGitRepository(config["data"]["path"]):
            rdata.clone(config["data"]["remote"], config["data"]["path"])

        devices_path = os.path.join(config["data"]["path"], "devices") 
        with open(devices_path, 'r') as f:
            match = list(filter(lambda x: x == config["device"]["id"],
                                f.read().splitlines()))
            
        if len(match) == 0:
            with open(devices_path, 'a') as f:
                f.write(config["device"]["id"])
            rdata.commit(config["data"]["path"], config["device"]["id"])

    else:
        raise Exception("<{0}> is not a 'rgit data' action")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dotfiles', action="store_true",
                        default=False, help="Assume dotfiles")
    possible_actions = ("help", "data", "raw")
    parser.add_argument('action', action="store", choices=possible_actions,
                        help="Action to perform")
    parser.add_argument('action_arg', action="store", nargs="?", default="",
                        help="Action argument")
    args = parser.parse_args()

    config = configparser.ConfigParser(config_defaults)
    config.read(config_path)
    config["data"]["path"] = os.path.expanduser(config["data"]["path"])
    config["rgit"]["gitRoot"] = os.path.expanduser(config["rgit"]["gitRoot"])
    requireConfigOpts(config, args)

    if args.action == "help":
        parser.print_help()
        sys.exit(0)
    
    if args.action == "raw":
        if args.action_arg == "":
            raise Exception("No path provided for 'raw' action.")
        rgitRawAction(config, args.action_arg, args.dotfiles)
        sys.exit(0)

    if args.action == "data":
        if args.action_arg == "":
            raise Exception("No argument provided for 'data' action.")
        rgitDataAction(config, args.action_arg, args.dotfiles)
        sys.exit(0)

    raise Exception("Ass clown")


if __name__ == "__main__":
    main()
