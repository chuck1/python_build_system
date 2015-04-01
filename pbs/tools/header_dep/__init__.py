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

g_proj = Project(__file__, 'root')

parser = argparse.ArgumentParser()
parser.add_argument("-d", help="directory", default=".")
parser.add_argument("-p", help="path prefix for label")
parser.add_argument("-c", action='store_true', help="do the precompiling")
parser.add_argument("-r", action='store_true', help="render dot")
parser.add_argument("-v", action='store_true', help="verbose")
parser.add_argument("-s", action='store_true', help="display system headers")
args = parser.parse_args()

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

#G = make_graph(g_proj, args, )
G = make_graph(proj2, args, )

if args.r:
    cmd = ["dot", "-Tpng", "header_dep.dot", "-oheader_dep.png"]
    subprocess.call(cmd)

with open("header_files.txt", 'w') as f:
    graph_analysis(G, f)

