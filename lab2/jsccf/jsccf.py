__version__ = "0.7.0"

import glob
import logging
import os
import argparse

from jsccf.jslexer import lex_file
from jsccf.jsrename import Renamer


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
    ap.add_argument('-fix', '--fix', action='store_true', help="Fix and save result files output <no-args>")

    args = ap.parse_args()
    logging.info(args)

    os.makedirs(args.out_log, exist_ok=True)

    files = file_args_handler(args)
    logging.info(f"Analysing {len(files)} files..")
    code_tree = analyse(files, args)
    logging.info(f"Generated code tree")

    renames = Renamer()
    logging.info(f"Searching declarations..")
    renames.find_declarations(code_tree, args)

    for dec in renames.declarations:
        print(dec)

    logging.info(f"Found declarations")
    logging.info(f"Searching references..")
    renames.build_references(code_tree, args)
    logging.info(f"Found references")
    logging.info(f"Finding errors..")
    errors, changes = renames.rename(code_tree, args)
    logging.info(f"Found {len(errors)} errors")

    if args.verify:
        logging.info(f"Writing log..")
        with open(os.path.join(args.out_log, 'verification.log'), 'w') as file:
            for e in errors:
                file.write(e.__str__() + "\n")

    if args.fix:
        logging.info(f"Applying changes..")
        with open(os.path.join(args.out_log, 'fixing.log'), 'w') as file:
            for c in changes:
                file.write(c.__str__() + "\n")

        for f, c in code_tree.items():
            s = ""
            for t in c:
                s += t.text
            with open(f, 'w') as file:
                file.write(s)

    logging.info(f"Complete!")


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
    return files


def project_handler(args):
    res = []
    for subdir, dirs, files in os.walk(args.p):
        for file in files:
            if file.endswith('.js'):
                res.append(os.path.join(subdir, file))
    return res


def directory_handler(args):
    res = []
    for file in os.listdir(args.d):
        if file.endswith('.js'):
            res.append(os.path.join(args.d, file))
    return res


def file_handler(args):
    return glob.glob(args.f)


def analyse(files, args):
    code_tree = {}
    for f in files:
        if f.endswith(".js"):
            # print(f)
            with open(f, 'r', encoding='utf-8') as file:
                file_code = file.read()
            tokens = lex_file(file_code, args)
            code_tree[f] = tokens

    return code_tree
