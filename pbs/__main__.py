import asyncio
import logging
import logging.config
import argparse
import re
import os
import shutil

import crayons
import pymake
import pbs
import pbs.command


async def make(args):
    await pbs.command.make(args.file, args.target)

async def Find(args):
    
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

async def new_class(args):

    f = args.file
    d = os.path.dirname(f)

    pymake.makedirs(d)

    src = os.path.join(pbs.BASE_DIR, "templates2", "CHeader.hpp_in")
    dst = f

    if os.path.exists(dst):
        print('file exists')
        return

    shutil.copyfile(src, dst)

#######################################

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_make = subparsers.add_parser('make')
parser_make.add_argument('file')
parser_make.add_argument('target', nargs='*')
parser_make.set_defaults(func=make)

parser_find = subparsers.add_parser('find')
parser_find.add_argument('pattern')
parser_find.add_argument('--move')
parser_find.set_defaults(func=Find)

parser_make = subparsers.add_parser('new_class')
parser_make.add_argument('file')
parser_make.set_defaults(func=new_class)





FMT_STRING = "%(name)14s %(levelname)7s %(message)s"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'basic'
            },
        },
    'loggers': {
        'pymake': {
            'handlers': ['console'],
            'level': logging.INFO,
            'propagate': False,            
            },
        'pbs': {
            'handlers': ['console'],
            'level': logging.INFO,
            'propagate': False,            
            },
        },
    'formatters': {"basic": {"format": FMT_STRING}}
    }

logging.config.dictConfig(LOGGING)








def help_(_):
    parser.print_help()

parser.set_defaults(func=help_)

args = parser.parse_args()

loop = asyncio.get_event_loop()

loop.run_until_complete(args.func(args))



