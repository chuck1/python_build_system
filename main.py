#!/usr/bin/env python3

import argparse
import pbs2
import pymake
import re
import os
import shutil

def Make(args):
    p = pbs2.Project()
    
    p.execfile(args.file)
    
    m = pymake.Makefile()
    
    m.rules += list(p.rules())
    
    try:
        if args.target:
            m.make(target=args.target)
        else:
            m.make(target='all')
    except pymake.BuildError as ex:
        print(ex)

def Find(args):
    
    #print 'Find',repr(args.pattern)

    pat = re.compile(args.pattern)

    for root, dirs, files in os.walk('.'):
        for f in files:
            f = os.path.join(root, f)

            m = pat.match(f)

            if m:
                print(f)
                #print m.groups()
                
                if args.move:
                    dst = re.sub(args.pattern, args.move, f)
                    print('move', repr(dst))
                    shutil.move(f, dst)

#######################################

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_make = subparsers.add_parser('make')
parser_make.add_argument('file')
parser_make.add_argument('target', nargs='*')
parser_make.set_defaults(func=Make)

parser_find = subparsers.add_parser('find')
parser_find.add_argument('pattern')
parser_find.add_argument('--move')
parser_find.set_defaults(func=Find)

def help_(_):
    parser.print_help()

parser.set_defaults(func=help_)

args = parser.parse_args()

args.func(args)



