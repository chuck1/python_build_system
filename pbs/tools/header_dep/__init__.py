#!/usr/bin/env python

import pickle
import re
import os
import glob
import myos
import sys
import subprocess
import argparse
import networkx as nx
import logging

import func
import graph

import pbs.Project
import pbs.func

def header_dep_func(args):

    # preliminaries
    if args.v:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # get and setup project
    d = pbs.func.read_config_file()

    project = pbs.Project.Project(d['root'], None)
    
    project.execute()

    for n,p in project.projects.items():

        print n
        print "  c_files"
        print "    "+"\n    ".join(p.get_c_files())

    
        """
        if args.c:
            c_files = func.get_c_files(args)
            
            logging.debug("\n".join(c_files))
    
            for f in c_files:
                func.precom(f)
        """

        #pre3_files = list(myos.glob(".*\.pre3$", args.d))
        pre3_files = list(p.get_pre3_files())
    
        logging.info("number of precompiler files: {}".format(len(pre3_files)))
  
        if not pre3_files:
            return

        proj2 = func.Pre3(__file__, 'root')
    
        func.combine_projects(pre3_files, proj2)
    
        G = graph.make_graph(proj2, args, )
   
    

        if args.r:
            cmd = ["dot", "-Tpng", "header_dep.dot", "-oheader_dep.png"]
            subprocess.call(cmd)
        
        with open("header_files.txt", 'w') as f:
            graph.graph_analysis(G, f)


