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

from func import *

def header_dep_func(args):

    if args.v:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    if args.c:
        c_files = get_c_files(args)
        
        for f in c_files:
            precom(f)
     
    proj_files = list(myos.glob(".*\.pre2\.pre_proj$", args.d))
    
    logging.info("number of precompiler files: {}".format(len(proj_files)))
    
    proj2 = Project(__file__, 'root')
    
    combine_projects(proj_files, proj2)
    
    G = make_graph(proj2, args, )
    
    if args.r:
        cmd = ["dot", "-Tpng", "header_dep.dot", "-oheader_dep.png"]
        subprocess.call(cmd)
    
    with open("header_files.txt", 'w') as f:
        graph_analysis(G, f)


