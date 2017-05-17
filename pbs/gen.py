#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect
#import myos

import pbs.classes.Static
import pbs.settings
import pbs.Project

def gen_func(args):
    project = pbs.Project.Project(os.path.abspath(args.root), args)

    project.save_config()

    project.do()

def func_bundle(args):
    d = pbs.func.read_config_file()
    
    project = pbs.Project.Project(d['root'], args)

    for name,p in project.projects.items():
        #print name
        #print p.inc_dir
        #print p.root
        in_files = list(p.get_h_in_files())
        for f in in_files:
            r = os.path.relpath(f, p.inc_dir)
            r2,_ = os.path.splitext(r)
            #print "  "+r
            #print "  "+r2
            src = f
            dst = os.path.join(p.root,'build','link',r2)
            #print "  {} --> {}".format(dst,src)
            
            fldr,_ = os.path.split(dst)

            try:
                os.makedirs(fldr)
            except:
                pass

            try:
                os.symlink(src, dst)
            except:
                pass

    project.bundle()

