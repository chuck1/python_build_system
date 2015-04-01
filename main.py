#!/usr/bin/env python

import argparse

import pbs
import pbs.gen

def gen(args):
    pbs.gen.gen_func(args)

def header_check(args):
    pbs.tools.header_checker.func(args)

def header_dep(args):
    pbs.tools.header_dep.func(args)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_gen = subparsers.add_parser('gen')
parser_gen.add_argument('root')
parser_gen.add_argument('-p', nargs=3)
parser_gen.set_defaults(func=gen)

args = parser.parse_args()
args.func(args)



