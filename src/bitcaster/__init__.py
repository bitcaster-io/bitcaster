from functools import lru_cache

NAME = 'bitcaster'
VERSION = __version__ = '0.3.0a8'
__author__ = 'Stefano Apostolico'


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

    from django.conf import settings
    if settings.ON_PREMISE:
        deployement = '(onpremise)'
    else:
        deployement = ''

    return f'{VERSION} {deployement} {commit} '


@lru_cache(1)
def get_git_status(clean='(nothing to commit)', dirty='(uncommitted changes)'):
    import subprocess
    try:
        uncommited = subprocess.check_output(['git', 'status', '-s'],
                                             stderr=None)
        return dirty if uncommited else clean
    except (subprocess.CalledProcessError, FileNotFoundError):  # pragma: no-cover
        return ''
