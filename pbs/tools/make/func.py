import os
import sys
import re
import glob
import subprocess
import logging

import pbs.func

import pbs.tools.make


def func(args):
    #print "make function"
    d = pbs.func.read_config_file()
    
    root = d['root']
    
    project = pbs.Project.Project(root, args)
    
    project.do()
   
    if args.v:
        logging.basicConfig(level=logging.DEBUG)

    m = pbs.tools.make.Makefile(project, True)

    for n,p in project.projects.items():
        #print "project", n
    
        #for r in p.reqs:
        #    print "  "+r.l.name

        #print p.root
        #print p.get_build_dir()

        m.targets += list(p.get_make_targets())
        m.targets += list(p.get_make_targets_0())

    m.targets.append(pbs.tools.make.Target(
        'all',
        list(p.name for p in project.projects.values()),
        None))

    #m.print_dep('all')
    m.make('all')

    #m.print_info()

