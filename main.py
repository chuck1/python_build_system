#!/usr/bin/env python

import argparse

import pbs
import pbs.gen
import pbs.clean
import pbs.tools.header_dep.pre2
import pbs.tools.header_dep.pre3
import pbs.tools.pkg
import pbs.tools.make.func

def gen(args):
    pbs.gen.gen_func(args)
def make(args):
    pbs.tools.make.func.func(args)
def clean(args):
    pbs.clean.func_clean(args)
def header_check(args):
    pbs.tools.header_checker.func(args)
def header_dep(args):
    pbs.tools.header_dep.header_dep_func(args)
def pre2(args):
    pbs.tools.header_dep.pre2.pre2_func(args)
def pre3(args):
    pbs.tools.header_dep.pre3.pre3_func(args)
def pkg(args):
    pbs.tools.pkg.pkg_func(args)

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
parser_pre2.add_argument("filename_in")
parser_pre2.add_argument("filename_out")
parser_pre2.set_defaults(func=pre2)

parser_pre3 = subparsers.add_parser('pre3')
parser_pre3.add_argument("filename_in")
parser_pre3.add_argument("filename_out")
parser_pre3.set_defaults(func=pre3)

parser_pkg = subparsers.add_parser('pkg')
parser_pkg.add_argument("component")
parser_pkg.set_defaults(func=pkg)

parser_clean = subparsers.add_parser('clean')
parser_clean.set_defaults(func=clean)

parser_make = subparsers.add_parser('make')
parser_make.set_defaults(func=make)
parser_make.add_argument("-v", action='store_true', help="verbose")

args = parser.parse_args()
args.func(args)



