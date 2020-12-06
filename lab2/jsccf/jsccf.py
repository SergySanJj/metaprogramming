__version__ = "0.0.1"

import logging
import os
import argparse


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
    args = ap.parse_args()

    os.makedirs(args.out_log, exist_ok=True)
    # TODO: add file versions
    logger.addHandler(logging.FileHandler(os.path.join(args.out_log, '_verification.log'), 'w'))

    logging.info(f'Parser args')
    logging.info(args)
