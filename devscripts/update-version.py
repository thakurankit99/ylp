#!/usr/bin/env python3

# Allow direct execution
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import argparse
import contextlib
import sys
from datetime import datetime

from devscripts.utils import read_version, run_process, write_file


def get_new_version(version, revision):
    if not version:
        version = datetime.utcnow().strftime('%Y.%m.%d')

    if revision:
        assert revision.isdigit(), 'Revision must be a number'
    else:
        old_version = read_version().split('.')
        if version.split('.') == old_version[:3]:
            revision = str(int((old_version + [0])[3]) + 1)

    return f'{version}.{revision}' if revision else version


def get_git_head():
    with contextlib.suppress(Exception):
        return run_process('git', 'rev-parse', 'HEAD').stdout.strip()


VERSION_TEMPLATE = '''\
# Autogenerated by devscripts/update-version.py

__version__ = {version!r}

RELEASE_GIT_HEAD = {git_head!r}

VARIANT = None

UPDATE_HINT = None

CHANNEL = {channel!r}
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update the version.py file')
    parser.add_argument(
        '-c', '--channel', default='stable',
        help='Select update channel (default: %(default)s)')
    parser.add_argument(
        '-o', '--output', default='yt_dlp/version.py',
        help='The output file to write to (default: %(default)s)')
    parser.add_argument(
        'version', nargs='?', default=None,
        help='A version or revision to use instead of generating one')
    args = parser.parse_args()

    git_head = get_git_head()
    version = (
        args.version if args.version and '.' in args.version
        else get_new_version(None, args.version))
    write_file(args.output, VERSION_TEMPLATE.format(
        version=version, git_head=git_head, channel=args.channel))

    print(f'version={version} ({args.channel}), head={git_head}')