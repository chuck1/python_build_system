#!/usr/bin/env python

import argparse

from func import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    proj = Project(__file__, args.filename)

    pre2_to_pre3(args.filename, proj)

    save_proj(proj)

