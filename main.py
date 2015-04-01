#!/usr/bin/env python

import argparse

import pbs
import pbs.gen
import pbs.tools.header_dep.pre2
import pbs.tools.header_dep.pre3

def gen(args):
    pbs.gen.gen_func(args)

def header_check(args):
    pbs.tools.header_checker.func(args)
def header_dep(args):
    pbs.tools.header_dep.header_dep_func(args)
def pre2(args):
    pbs.tools.header_dep.pre2.pre2_func(args)
def pre3(args):
    pbs.tools.header_dep.pre3.pre3_func(args)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_gen = subparsers.add_parser('gen')
parser_gen.add_argument('root')
parser_gen.add_argument('-p', nargs=3)
parser_gen.set_defaults(func=gen)

parser_hd = subparsers.add_parser('header_dep')
parser_hd.add_argument("-d", help="directory", default=".")
parser_hd.add_argument("-p", help="path prefix for label")
parser_hd.add_argument("-c", action='store_true', help="do the precompiling")
parser_hd.add_argument("-r", action='store_true', help="render dot")
parser_hd.add_argument("-v", action='store_true', help="verbose")
parser_hd.add_argument("-s", action='store_true', help="display system headers")
parser_hd.set_defaults(func=header_dep)

parser_pre2 = subparsers.add_parser('pre2')
parser_pre2.add_argument("filename")
parser_pre2.set_defaults(func=pre2)

parser_pre3 = subparsers.add_parser('pre3')
parser_pre3.add_argument("filename")
parser_pre3.set_defaults(func=pre3)

args = parser.parse_args()
args.func(args)



