import subprocess
from functools import lru_cache

NAME = 'mercury'
VERSION = __version__ = '0.1'
__author__ = 'Stefano Apostolico'


@lru_cache(1)
def get_full_version(git_commit=True):
    commit = ""
    if git_commit:
        res = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
        commit = "-" + res.decode('utf8')[:-1]
    return f"{VERSION}{commit}"


@lru_cache(1)
def get_git_status(clean=" (nothing to commit)", dirty=" (uncommitted changes)"):
    uncommited = subprocess.check_output(['git', 'status', '-s'])
    return dirty if uncommited else clean
