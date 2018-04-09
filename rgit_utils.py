#!/usr/bin/env python3

import contextlib
import subprocess
import os

@contextlib.contextmanager
def chdirGuard(path):
    prev_dir = os.getcwd()
    os.chdir(path)
    try: yield
    finally: os.chdir(prev_dir)


def isGitRepository(path, policy="return"):
    dir_git = os.path.join(path, ".git")
    ret = os.path.isdir(dir_git)

    if policy in ("return", "bool"):
        return ret
    elif policy in ("require", "throw", "raise"):
        if not ret:
            raise Exception("<{0}> directory does not exist!".format(dir_git))
    else:
        raise Exception("Fatal - unknown policy <{0}>!".format(policy))


def listDirFilterOnlyDirectories(path):
    all_files = os.listdir(path)
    return list(filter(lambda x: os.path.isdir(os.path.join(path, x)), all_files))


def _idFromHttps(remote):
    if remote.startswith("https://"):
        remote = remote[8:]
    if remote.endswith(".git"):
        remote = remote[:-4]
    return remote


def _idFromSsh(remote):
    if not remote.endswith(".git"):
        raise Exception("Fatal in _idFromSsh")
    after_at = remote.split('@')[1]
    remote = '/'.join(after_at.split(':'))
    return remote[:-4]
    

def getRepoId(directory, git_cmd="git"):
    isGitRepository(directory, policy="require")

    cmd = git_cmd + " remote -v"
    output = subprocess.check_output(cmd, shell=True, cwd=directory)
    
    output = output.splitlines()
    output = list(filter(lambda x: b"origin" in x, output))[0] 
    remote = output.split()[1].decode("utf-8")

    print(remote)
    if '@' in remote:
        return _idFromSsh(remote)
    return _idFromHttps(remote)
     

def isBlacklisted(repo_id):
    global _BLACKLIST
    if not _BLACKLIST:
        raise Exception("Blacklist has not been initialized")

    server = repo_id.split('/')[0]
    if server in _BLACKLIST:
        return True
    return False


def setBlacklist(blacklist_str):
    global _BLACKLIST
    _BLACKLIST = blacklist_str.split(',') 

_BLACKLIST = None
       




