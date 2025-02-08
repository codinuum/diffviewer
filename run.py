#!/usr/bin/env python3

import os
import sys
import re
from subprocess import call

PLATFORM = sys.platform

VIEWER_APP_DIR_PAT = re.compile(f'DiffViewer-{PLATFORM}-([0-9a-z]+)')


if __name__ == '__main__':
    if PLATFORM not in ['darwin', 'linux']:
        print(f'not supported: {PLATFORM}')
        sys.exit(1)

    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(description='DiffViewer driver',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('file0', type=str, metavar='ORIGINAL',
                        help='original source file (path or SHA1)')

    parser.add_argument('file1', type=str, metavar='MODIFIED',
                        help='modified source file (path or SHA1)')

    parser.add_argument('--git', dest='git_repo', default=None,
                        metavar='DIR', type=str,
                        help='specify git repository path')

    parser.add_argument('--path0', dest='path0', default=None,
                        metavar='PATH', type=str,
                        help='specify original file path')

    parser.add_argument('--path', dest='path', default=None,
                        metavar='PATH', type=str,
                        help='specify modified file path')

    parser.add_argument('-c', '--cache', dest='cache', default=None,
                        metavar='DIR', type=str, help='specify cache path')

    parser.add_argument('-l', '--local-cache-name', dest='local_cache_name',
                        default=None, metavar='NAME', type=str,
                        help='specify local cache name')

    parser.add_argument('--foreground', dest='foreground', action='store_true',
                        help='do not fork')

    args = parser.parse_args()

    opt = ''
    if args.cache is not None:
        apathc = os.path.abspath(args.cache)
        opt = f' --cache {apathc}'

    if args.local_cache_name is not None:
        opt += f' --localcachename {args.local_cache_name}'

    if args.git_repo is None:
        apath0 = os.path.abspath(args.file0)
        apath1 = os.path.abspath(args.file1)
        opt += f' --file0 {apath0} --file1 {apath1}'
    elif args.path is not None:
        apathr = os.path.abspath(args.git_repo)
        opt += f' --git {apathr} --oid0 {args.file0} --oid1 {args.file1}'
        opt += f' --path {args.path}'
        if args.path0 is not None:
            opt += f' --path0 {args.path0}'
    else:
        print('(modified) file path required')
        parser.print_help()
        sys.exit(1)

    here = os.path.dirname(sys.argv[0])
    viewer_app_path = None

    for fn in os.listdir(here):
        if VIEWER_APP_DIR_PAT.match(fn):
            if PLATFORM == 'darwin':
                viewer_app_path = os.path.join(here, fn, 'DiffViewer.app')

            elif PLATFORM == 'linux':
                viewer_app_path = os.path.join(here, fn, 'DiffViewer')

    if viewer_app_path is None:
        print('App not found')
    else:
        if args.foreground:
            if PLATFORM == 'darwin':
                cmdp = os.path.join(viewer_app_path,
                                    '/Contents/MacOS/DiffViewer')

            elif PLATFORM == 'linux':
                cmdp = viewer_app_path

            cmd = f'{cmdp} --args{opt}'
        else:
            app = viewer_app_path

            if PLATFORM == 'darwin':
                cmd = f'open -n {app} --args{opt}'
            elif PLATFORM == 'linux':
                cmd = f'{app} --args{opt} &'

        try:
            rc = call(cmd, shell=True)
        except Exception as e:
            print('failed to execute: ', e)
