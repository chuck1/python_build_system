#!/usr/bin/env python

import argparse

import pbs.tools.header_dep.func

def pre3_func(args):

    proj = pbs.tools.header_dep.func.Project(__file__, args.filename)

    pbs.tools.header_dep.func.pre2_to_pre3(args.filename, proj)

    pbs.tools.header_dep.func.save_proj(proj)

