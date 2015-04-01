#!/usr/bin/env python

import argparse

from func import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    pre_to_pre2(args.filename)

