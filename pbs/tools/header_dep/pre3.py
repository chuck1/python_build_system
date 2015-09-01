#!/usr/bin/env python

import argparse

import pbs.tools.header_dep.func

def pre3_func(args):

    pbs.tools.header_dep.func.pre2_to_pre3(args.filename_in, args.filename_out)




