import pathlib
from functools import lru_cache

DIR = pathlib.Path(__file__).parent

NAME = 'bitcaster'
VERSION = __version__ = '0.38.0a1'
__author__ = 'Bitcaster Team'


@lru_cache(1)
def get_full_version(git_commit=True):
    commit = ''
    if git_commit:
        import subprocess
        try:
            res = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
                                          stderr=None)
            commit = '-' + res.decode('utf8')[:-1]
        except (subprocess.CalledProcessError, FileNotFoundError):  # pragma: no-cover
            pass

    return f'{VERSION} {commit} '


@lru_cache(1)
def get_git_status(clean='(nothing to commit)', dirty='(uncommitted changes)'):
    import subprocess
    try:
        uncommited = subprocess.check_output(['git', 'status', '-s'],
                                             stderr=None)
        return dirty if uncommited else clean
    except (subprocess.CalledProcessError, FileNotFoundError):  # pragma: no-cover
        return ''
