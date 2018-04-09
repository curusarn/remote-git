#!/usr/bin/env python3

import shutil
import subprocess
import sys
import os

import rgit_utils as rutils


_RECORD_CMDS = []

def initRecordCmds(git_depth):
    global _RECORD_CMDS
    _RECORD_CMDS.append((' rev-parse HEAD', "HEAD"))
    _RECORD_CMDS.append((' rev-parse --short HEAD', "HEAD_short"))
    _RECORD_CMDS.append((' status --short', "status_short"))
    _RECORD_CMDS.append((' status', "status"))
    _RECORD_CMDS.append((' cherry -v', "cherry_v"))
    _RECORD_CMDS.append((' log --max-count {0} --graph --oneline'.format(git_depth), "log_graph_oneline"))
    _RECORD_CMDS.append((' log --max-count {0} --oneline'.format(git_depth), "log_oneline"))
    _RECORD_CMDS.append((' log --max-count {0} --pretty="%H"'.format(git_depth), "log_H"))
    _RECORD_CMDS.append((' branch --verbose', "branch_verbose"))


def getRecordCmds(git_cmd="git"):
    global _RECORD_CMDS
    for cmd in _RECORD_CMDS:
        yield (git_cmd + cmd[0], cmd[1])


def getRecordCmdsDiffs(repo_path, git_cmd="git"):
    output = subprocess.check_output(git_cmd + " cherry -v",
                                     shell=True, cwd=repo_path)
    for line in output.splitlines():
        hash = line.split()[1]
        yield ("{0} diff {1}^ {1}".format(git_cmd, hash), "diff/" + hash)

    yield (git_cmd + " diff --staged", "diff/staged")
    yield (git_cmd + " diff", "diff/unstaged")


def clone(remote, path):
    if not os.path.exists(path):
        os.makedirs(path)

    cmd = ("git", "clone", remote, path)
    print(cmd)
    print("[rgit] clone")
    subprocess.call(cmd, cwd='/')
    

def pull(remote, path):
    if not rutils.isGitRepository(path):
        clone(remote, path)

    cmd = ("git", "pull")
    print("[rgit] pull")
    subprocess.call(cmd, cwd=path)
    

def _recordGitCmd(cmd, filename, path, cwd_path):
    file_path = os.path.join(path, filename)
    output = subprocess.check_output(cmd, shell=True, cwd=cwd_path)\
             .decode("utf-8")
    with open(file_path, 'w') as f:
        f.write(output)


def _recordRepository(repo_path, data_path, device_id, git_cmd="git"):
    repo_id = rutils.getRepoId(repo_path)

    path = os.path.join(data_path, "data", repo_id, device_id)

    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)

    for cmd in getRecordCmds(git_cmd):
        _recordGitCmd(cmd[0], cmd[1], path, repo_path)

    diff_path = os.path.join(path, "diff")
    os.makedirs(diff_path)

    for cmd in getRecordCmdsDiffs(repo_path, git_cmd):
        _recordGitCmd(cmd[0], cmd[1], path, repo_path)


def record(git_root, data_path, device_id, git_depth, dotfiles_git_cmd=None):
    rutils.isGitRepository(data_path, policy="require")

    print("[rgit] record")
    repositories = rutils.listDirFilterOnlyDirectories(git_root)

    for repo in repositories:
        repo_path = os.path.join(git_root, repo)

        if not rutils.isGitRepository(repo_path):
            continue

        repo_id = rutils.getRepoId(repo_path)
        if not rutils.isBlacklisted(repo_id):
            _recordRepository(repo_path, data_path, device_id)

    # dotfiles
    if dotfiles_git_cmd:
        _recordRepository(".", data_path, device_id, dotfiles_git_cmd)


def commit(path, device_id, commit_msg=None):
    rutils.isGitRepository(path, policy="require")

    if commit_msg is None:
        commit_msg = "Device: {0}".format(device_id)

    cmd = ("git", "add", ".")
    print("[rgit] add changes")
    subprocess.check_call(cmd, cwd=path)

    cmd = ("git", "commit", "-m", commit_msg)
    print("[rgit] commit")
    subprocess.call(cmd, cwd=path)


def push(path):
    rutils.isGitRepository(path, policy="require")

    cmd = ("git", "push")
    print("[rgit] push")
    subprocess.check_call(cmd, cwd=path)


def purge(path):
    print("[rgit] purge")
    #path = os.path.join(path, "data")
    if os.path.exists(path):
        print("[rgit] deleting <{0}>".format(path))
        shutil.rmtree(path)


def setup(remote, path, device_id):
    print("[rgit] setup")
    print(remote)
    print(path)
    print(device_id)
    if not os.path.exists(path) or not rutils.isGitRepository(path):
        clone(remote, path)

    devices_path = os.path.join(path, "devices") 
    with open(devices_path, 'r') as f:
        match = list(filter(lambda x: x == device_id,
                            f.read().splitlines()))

    if len(match) == 0:
        with open(devices_path, 'a') as f:
            f.write(device_id)
        commit(path, device_id)
