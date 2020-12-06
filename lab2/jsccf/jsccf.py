__version__ = "0.0.1"

import glob
import logging
import os
import argparse

from jsccf.jslexer import lex_file


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    ap = argparse.ArgumentParser(description="Renaming and documenting tool for JavaScript")
    ap.add_argument('-p', type=str, default=None, help="Fix/Verify .js project in <str:path> dir")
    ap.add_argument('-d', type=str, default=None, help="Fix/Verify .js files in <str:path> dir")
    ap.add_argument('-f', type=str, default=None, help="Fix/Verify .js file by <str:path> path")
    ap.add_argument('--out-log', type=str, default='.', help="Output log files path")

    ap.add_argument('-v', '--verify', action='store_true', help="Use verification <no-args>")
    ap.add_argument('-fix', action='store_true', help="Fix and save result files output <no-args>")
    ap.add_argument('-use-dollar', action='store_true',
                    help="Variables can have dollar sign as first character <no-args>")
    args = ap.parse_args()

    os.makedirs(args.out_log, exist_ok=True)
    # TODO: add file versions
    logger.addHandler(logging.FileHandler(os.path.join(args.out_log, '_verification.log'), 'w'))

    logging.info(f'Parser args')
    logging.info(args)

    files = file_args_handler(args)
    code_tree = analyse(files, args)
    #print(code_tree)


def file_args_handler(args):
    file_args = {'p': project_handler, 'd': directory_handler, 'f': file_handler}

    handler_func = None
    cnt = 0

    for arg, handler in file_args.items():
        if getattr(args, arg) is not None:
            handler_func = handler
            cnt += 1
    if cnt == 0:
        raise ValueError('Please specify single (-p | -d | -f) arg')
    if cnt > 1:
        raise ValueError('Arguments are ambiguous, please specify single(-p | -d | -f) arg')

    files = handler_func(args)
    logging.info(f'Analysing {len(files)} files')
    return files


def project_handler(args):
    res = []
    for subdir, dirs, files in os.walk(args.p):
        for file in files:
            res.append(os.path.join(subdir, file))
    return res


def directory_handler(args):
    res = []
    for file in os.listdir(args.d):
        if file.endswith('.js'):
            res.append(file)
    return res


def file_handler(args):
    return glob.glob(args.f)


def analyse(files, args):
    code_tree = {}
    for f in files:
        print(f)
        with open(f, 'r') as file:
            file_code = file.read()
        tokens = lex_file(file_code, args)
        for t in tokens:
            print(t)
        code_tree[f] = tokens

    return code_tree
