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


def _idFromHttps(remote):
    if not remote.endswith(".git"):
        raise Exception("Fatal in _idFromHttps")
    return remote[:-4]


def _idFromSsh(remote):
    if not remote.endswith(".git"):
        raise Exception("Fatal in _idFromHttps")
    after_at = split('@')[1]
    remote = after_at.split(':').join('/')
    return remote[:-4]
    

def getRepoId(directory, git_cmd="git"):
    dir_git = os.path.join(directory,".git")
    if not os.path.isdir(dir_git):
        raise Exception("<{0}> directory does not exist!".format(dir_git))

    cmd = git_cmd + " remote -v"
    with chdirGuard(directory):
        output = subprocess.check_output(cmd, shell=True)
    
    output = output.splitlines()
    output = list(filter(lambda x:"(origin)" in x, output))[0] 
    remote = output.split()[1]
    print(remote)

    if '@' in remote:
        return _idFromSsh
    else
        return _idFromHttps
     


