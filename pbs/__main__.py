#!/usr/bin/env python3
import asyncio
import logging
import argparse
import re
import os
import shutil
import pymake
import pbs
from mybuiltins import ason

class Decoder(ason.Decoder):
    async def parse_function(self, k, args, kwargs, mc=None):

        _ = {
            #'/eval': _eval,
            #'/ReqFile':     pymake.ReqFile,
            #'/ReqDoc':      pymake.req.ReqDoc,
            #'/Array':       functools.partial(coil_testing.array.Array, mc),
            #'/Series':      functools.partial(coil_testing.coil_calc.process.series.Series, mc),
            #'/read_pickle': functools.partial(_read_pickle, mc),
            }

        f = _[k]

        try:

            res = f(*args, **kwargs)

            if asyncio.iscoroutine(res):
                return await res

        except Exception as e:
            logger.error(f'f      = {f!r}')
            logger.error(f'args   = {args!r}')
            logger.error(f'kwargs = {kwargs!r}')
            logger.error(f'e      = {e!r}')
            raise

        return res


async def Make(args):
    p = pbs.Project()
    
    p.execfile(args.file)
    
    m = pymake.Makefile()
    
    m.rules += list(p.rules())

    m.decoder = Decoder()

    try:
        if args.target:
            await m.make(target=args.target)
        else:
            await m.make(target='all')
    except pymake.BuildError as ex:
        print(ex)

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
parser_make.set_defaults(func=Make)

parser_find = subparsers.add_parser('find')
parser_find.add_argument('pattern')
parser_find.add_argument('--move')
parser_find.set_defaults(func=Find)

parser_make = subparsers.add_parser('new_class')
parser_make.add_argument('file')
parser_make.set_defaults(func=new_class)




logging.basicConfig(level=logging.INFO)








def help_(_):
    parser.print_help()

parser.set_defaults(func=help_)

args = parser.parse_args()

loop = asyncio.get_event_loop()

loop.run_until_complete(args.func(args))



