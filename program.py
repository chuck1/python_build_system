#!/usr/bin/env python

import argparse
import pbs2
import pymake

def Make(args):
    p = pbs2.Project()
    
    p.execfile(args.file)
    
    m = pymake.Makefile()
    
    m.rules += list(p.rules())

    m.make('all')

#######################################

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_make = subparsers.add_parser('make')
parser_make.add_argument('file')
parser_make.set_defaults(func=Make)

args = parser.parse_args()

args.func(args)

